from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from groups.models import InsuranceGroup
from members.models import Member
from policy_management.models import Policy, PolicyApplication, PolicyStatus, CoverageType
from endorsements.models import Endorsement, EndorsementStatus
from renewals.models import Renewal, RenewalStatus
from claims.models import Claim, ClaimStatus
from billing.models import Invoice, Payment
from commissions.models import Commission, CommissionStatus
from accounts.models import ActivityLog
from accounts.serializers import ActivityLogSerializer


class DashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        upcoming_threshold = today + timedelta(days=60)

        # Filters by role if Group Manager or Policyholder
        policy_qs = Policy.objects.all()
        claim_qs = Claim.objects.all()
        invoice_qs = Invoice.objects.all()
        group_qs = InsuranceGroup.objects.all()
        member_qs = Member.objects.all()

        if user.role == 'GROUP_MANAGER':
            group_qs = group_qs.filter(manager=user)
            member_qs = member_qs.filter(group__manager=user)
            policy_qs = policy_qs.filter(group__manager=user)
            claim_qs = claim_qs.filter(policy__group__manager=user)
            invoice_qs = invoice_qs.filter(group__manager=user)
        elif user.role == 'POLICYHOLDER':
            member_qs = member_qs.filter(user=user)
            policy_qs = policy_qs.filter(policy_members__member__user=user).distinct()
            claim_qs = claim_qs.filter(member__user=user)
            invoice_qs = invoice_qs.filter(group__members__user=user).distinct()

        # 1. Metric Cards
        total_groups = group_qs.count()
        total_members = member_qs.count()
        total_policies = policy_qs.count()
        active_policies = policy_qs.filter(Q(status__iexact='ACTIVE') | Q(policy_status__iexact='ACTIVE')).count()

        pending_uw = PolicyApplication.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW', 'Submitted', 'Under Review']).count()
        pending_endorsements = Endorsement.objects.filter(Q(status=EndorsementStatus.PENDING) | Q(status='Pending')).count()
        upcoming_renewals = policy_qs.filter(
            Q(status__iexact='ACTIVE') | Q(policy_status__iexact='ACTIVE'),
            expiry_date__gte=today,
            expiry_date__lte=upcoming_threshold
        ).count()

        total_claims = claim_qs.count()
        pending_claims = claim_qs.filter(
            Q(status__in=[ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW, ClaimStatus.VERIFIED]) |
            Q(status__in=['SUBMITTED', 'UNDER_REVIEW', 'VERIFIED', 'Submitted', 'Under Review', 'Verified'])
        ).count()

        premium_collected = invoice_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
        outstanding_payments = invoice_qs.aggregate(Sum('balance_due'))['balance_due__sum'] or Decimal('0.00')
        total_commissions = Commission.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')

        # 2. Charts: Monthly Premium Collection (Past 12 months from actual payments)
        twelve_months_ago = today - timedelta(days=365)
        payments_by_month = (
            Payment.objects.filter(payment_date__gte=twelve_months_ago)
            .annotate(month=TruncMonth('payment_date'))
            .values('month')
            .annotate(collected=Sum('amount'))
            .order_by('month')
        )
        monthly_premium_chart = [
            {
                'month': p['month'].strftime('%b %Y') if p['month'] else 'N/A',
                'amount': float(p['collected'] or 0)
            }
            for p in payments_by_month
        ]

        # 3. Claims by Status Distribution
        claims_status_dist = (
            claim_qs.values('status')
            .annotate(count=Count('id'), total_val=Sum('claim_amount'))
            .order_by('-count')
        )
        claims_by_status = [
            {'status': c['status'], 'count': c['count'], 'amount': float(c['total_val'] or 0)}
            for c in claims_status_dist
        ]

        # 4. Policies by Category / Coverage Type
        policies_by_cat = (
            policy_qs.values('product__coverage_type')
            .annotate(count=Count('id'), total_sum=Sum('total_sum_insured'))
            .order_by('-count')
        )
        policies_by_category = [
            {
                'category': p['product__coverage_type'] or 'GENERAL',
                'count': p['count'],
                'sum_insured': float(p['total_sum'] or 0)
            }
            for p in policies_by_cat
        ]

        # 5. Group-wise Policy Distribution (Top 5 groups)
        group_dist = (
            policy_qs.values('group__name')
            .annotate(policies_count=Count('id'), total_premium=Sum('total_premium'))
            .order_by('-total_premium')[:5]
        )
        group_policy_distribution = [
            {
                'group': g['group__name'] or 'Unknown Group',
                'policies': g['policies_count'],
                'premium': float(g['total_premium'] or 0)
            }
            for g in group_dist
        ]

        # 6. Revenue vs Commission Comparison
        revenue_vs_commission = [
            {'name': 'Total Invoiced Premium', 'value': float(invoice_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)},
            {'name': 'Net Premium Collected', 'value': float(premium_collected)},
            {'name': 'Outstanding Premium', 'value': float(outstanding_payments)},
            {'name': 'Agent Commissions', 'value': float(total_commissions)},
        ]

        # 7. Recent Items
        recent_activities = ActivityLogSerializer(ActivityLog.objects.all()[:8], many=True).data

        upcoming_expirations = [
            {
                'id': p.id,
                'policy_number': p.policy_number,
                'group_name': p.group.name,
                'product_name': p.product.name,
                'expiry_date': p.expiry_date,
                'total_premium': p.total_premium
            }
            for p in policy_qs.filter(Q(status__iexact='ACTIVE') | Q(policy_status__iexact='ACTIVE')).order_by('expiry_date')[:5]
        ]

        recent_claims = [
            {
                'id': c.id,
                'claim_number': c.claim_number,
                'member_name': c.member.full_name,
                'policy_number': c.policy.policy_number,
                'claim_amount': c.claim_amount,
                'status': c.status,
                'incident_date': c.incident_date
            }
            for c in claim_qs.order_by('-id')[:5]
        ]

        recent_transactions = [
            {
                'id': p.id,
                'payment_reference': p.payment_reference,
                'payer_name': p.payer_name,
                'amount': p.amount,
                'payment_method': p.payment_method,
                'payment_date': p.payment_date,
                'invoice_number': p.invoice.invoice_number
            }
            for p in Payment.objects.all().order_by('-id')[:5]
        ]

        return Response({
            'metrics': {
                'total_groups': total_groups,
                'total_members': total_members,
                'total_policies': total_policies,
                'active_policies': active_policies,
                'pending_underwriting': pending_uw,
                'pending_endorsements': pending_endorsements,
                'upcoming_renewals': upcoming_renewals,
                'total_claims': total_claims,
                'pending_claims': pending_claims,
                'premium_collected': premium_collected,
                'outstanding_payments': outstanding_payments,
                'total_commissions': total_commissions,
            },
            'charts': {
                'monthly_premium': monthly_premium_chart,
                'claims_by_status': claims_by_status,
                'policies_by_category': policies_by_category,
                'group_distribution': group_policy_distribution,
                'revenue_vs_commission': revenue_vs_commission
            },
            'tables': {
                'recent_activities': recent_activities,
                'upcoming_expirations': upcoming_expirations,
                'recent_claims': recent_claims,
                'recent_transactions': recent_transactions
            }
        })


class PolicyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = Policy.objects.all().select_related('group', 'product')
        status_counts = policies.values('status').annotate(count=Count('id'), total_premium=Sum('total_premium'))
        product_counts = policies.values('product__name', 'product__coverage_type').annotate(count=Count('id'), total_sum=Sum('total_sum_insured'))
        return Response({
            'total_policies': policies.count(),
            'by_status': status_counts,
            'by_product': product_counts
        })


class ClaimReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claims = Claim.objects.all()
        by_status = claims.values('status').annotate(count=Count('id'), total_claimed=Sum('claim_amount'), total_settled=Sum('approved_amount'))
        by_type = claims.values('claim_type').annotate(count=Count('id'), total_claimed=Sum('claim_amount'))
        return Response({
            'total_claims': claims.count(),
            'by_status': by_status,
            'by_type': by_type
        })


class FinancialReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_invoiced = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        total_collected = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
        total_outstanding = Invoice.objects.aggregate(Sum('balance_due'))['balance_due__sum'] or Decimal('0.00')
        total_commissions = Commission.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        pending_commissions = Commission.objects.filter(status='PENDING').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        paid_commissions = Commission.objects.filter(status='PAID').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')

        return Response({
            'total_premium_invoiced': total_invoiced,
            'total_premium_collected': total_collected,
            'outstanding_premium': total_outstanding,
            'total_commissions': total_commissions,
            'pending_commissions': pending_commissions,
            'paid_commissions': paid_commissions,
        })
