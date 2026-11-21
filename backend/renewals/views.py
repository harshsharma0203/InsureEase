from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Renewal, RenewalStatus
from .serializers import RenewalSerializer
from policy_management.models import Policy, PolicyStatus, PolicyMember, PolicyVersion
from policy_management.serializers import PolicySerializer
from billing.models import Invoice
from accounts.permissions import log_activity
from accounts.models import Notification


class RenewalViewSet(viewsets.ModelViewSet):
    queryset = Renewal.objects.all().select_related('policy', 'policy__group', 'policy__product', 'renewed_policy', 'reviewed_by')
    serializer_class = RenewalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['renewal_number', 'policy__policy_number', 'policy__group__name', 'policy__product__name']
    ordering_fields = ['id', 'proposed_expiry_date', 'revised_premium', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(policy__group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(policy__policy_members__member__user=user).distinct()

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        count = Renewal.objects.count() + 1
        ren_num = f"REN-2026-{count:04d}"
        policy = serializer.validated_data.get('policy')

        # Calculate historical claims ratio
        claims_sum = policy.claims.filter(status='SETTLED').aggregate(Sum('approved_amount'))['approved_amount__sum'] or Decimal('0.00')
        ratio = Decimal('0.00')
        if policy.total_premium > Decimal('0.00'):
            ratio = ((claims_sum / policy.total_premium) * Decimal('100.00')).quantize(Decimal('0.01'))

        # Revised premium formula
        if ratio < Decimal('40.00'):
            factor = Decimal('0.95')  # 5% No claim bonus discount
        elif ratio <= Decimal('75.00'):
            factor = Decimal('1.00')  # Standard rate
        elif ratio <= Decimal('100.00'):
            factor = Decimal('1.10')  # 10% loading
        else:
            factor = Decimal('1.25')  # 25% high-loss loading

        prev_premium = policy.base_annual_premium
        revised = (prev_premium * factor).quantize(Decimal('0.01'))
        p_start = policy.expiry_date + timedelta(days=1)
        p_expiry = p_start + timedelta(days=365)

        instance = serializer.save(
            renewal_number=ren_num,
            previous_annual_premium=prev_premium,
            claims_ratio_percentage=ratio,
            revised_premium=revised,
            revised_sum_insured=policy.total_sum_insured,
            proposed_start_date=p_start,
            proposed_expiry_date=p_expiry,
            status=RenewalStatus.PENDING
        )
        log_activity(self.request.user, "Created Renewal Application", "renewals", f"Renewal {instance.renewal_number} created for Policy {policy.policy_number}.", self.request.META.get('REMOTE_ADDR'))

    @action(detail=False, methods=['get'])
    def approaching_expiry(self, request):
        today = date.today()
        threshold = today + timedelta(days=60)
        # Policies expiring within 60 days
        policies = Policy.objects.filter(
            status=PolicyStatus.ACTIVE,
            expiry_date__lte=threshold
        ).select_related('group', 'product')
        return Response(PolicySerializer(policies, many=True).data)

    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        renewal = self.get_object()
        renewal.reminder_count += 1
        renewal.last_reminder_sent = timezone.now()
        renewal.save()

        # Create system notification for group manager
        if renewal.policy.group.manager:
            Notification.objects.create(
                user=renewal.policy.group.manager,
                title="Policy Renewal Reminder",
                message=f"Reminder #{renewal.reminder_count}: Policy {renewal.policy.policy_number} is due for renewal on {renewal.policy.expiry_date}.",
                notification_type='WARNING',
                link=f"/renewals"
            )

        log_activity(request.user, "Sent Renewal Reminder", "renewals", f"Sent reminder #{renewal.reminder_count} for {renewal.renewal_number}.", request.META.get('REMOTE_ADDR'))
        return Response({"status": "Reminder sent successfully", "reminder_count": renewal.reminder_count})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        renewal = self.get_object()
        if renewal.status in [RenewalStatus.APPROVED, RenewalStatus.COMPLETED]:
            return Response({"error": "Renewal is already processed."}, status=status.HTTP_400_BAD_REQUEST)

        policy = renewal.policy
        policy.status = PolicyStatus.EXPIRED
        policy.save()

        # Issue renewed policy
        count = Policy.objects.count() + 1
        new_policy_num = f"POL-2026-{count:04d}"
        tax = (renewal.revised_premium * Decimal('0.18')).quantize(Decimal('0.01'))
        tot = renewal.revised_premium + tax

        renewed_policy = Policy.objects.create(
            policy_number=new_policy_num,
            application=policy.application,
            group=policy.group,
            product=policy.product,
            sum_insured_per_member=policy.sum_insured_per_member,
            total_members_covered=policy.total_members_covered,
            total_sum_insured=renewal.revised_sum_insured,
            base_annual_premium=renewal.revised_premium,
            tax_amount=tax,
            total_premium=tot,
            start_date=renewal.proposed_start_date,
            expiry_date=renewal.proposed_expiry_date,
            status=PolicyStatus.ACTIVE,
            terms_and_conditions=f"Renewed from historical policy {policy.policy_number}."
        )

        # Copy over active members
        active_members = policy.policy_members.filter(status='ACTIVE')
        for pm in active_members:
            PolicyMember.objects.create(
                policy=renewed_policy,
                member=pm.member,
                coverage_amount=pm.coverage_amount,
                individual_premium=(renewal.revised_premium / max(1, policy.total_members_covered)).quantize(Decimal('0.01')),
                effective_date=renewed_policy.start_date,
                status='ACTIVE'
            )

        # Create Version 1 for renewed policy
        PolicyVersion.objects.create(
            policy=renewed_policy,
            version_number=1,
            snapshot_data={
                'policy_number': renewed_policy.policy_number,
                'renewed_from': policy.policy_number,
                'claims_ratio': str(renewal.claims_ratio_percentage),
                'total_premium': str(renewed_policy.total_premium),
                'start_date': str(renewed_policy.start_date),
                'expiry_date': str(renewed_policy.expiry_date),
            },
            change_reason=f"Policy Renewal of {policy.policy_number} under {renewal.renewal_number}",
            effective_date=renewed_policy.start_date,
            created_by=request.user
        )

        # Generate Renewal Invoice
        inv_count = Invoice.objects.count() + 1
        Invoice.objects.create(
            invoice_number=f"INV-2026-{inv_count:04d}",
            policy=renewed_policy,
            group=renewed_policy.group,
            invoice_date=renewed_policy.start_date,
            due_date=renewed_policy.start_date + timedelta(days=30),
            subtotal_amount=renewal.revised_premium,
            tax_rate_percentage=Decimal('18.00'),
            tax_amount=tax,
            total_amount=tot,
            paid_amount=Decimal('0.00'),
            balance_due=tot,
            status='UNPAID',
            notes=f"Renewal premium invoice for {renewed_policy.policy_number} (Renewed from {policy.policy_number})"
        )

        renewal.renewed_policy = renewed_policy
        renewal.status = RenewalStatus.COMPLETED
        renewal.reviewed_by = request.user
        renewal.review_date = timezone.now()
        renewal.remarks = request.data.get('remarks', 'Renewal approved and new policy issued.')
        renewal.save()

        log_activity(request.user, "Approved Renewal & Issued Policy", "renewals", f"Policy {policy.policy_number} renewed as {renewed_policy.policy_number}.", request.META.get('REMOTE_ADDR'))
        return Response({
            "detail": "Renewal approved. Renewed policy issued.",
            "renewal": RenewalSerializer(renewal).data,
            "renewed_policy": PolicySerializer(renewed_policy).data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        renewal = self.get_object()
        renewal.status = RenewalStatus.REJECTED
        renewal.reviewed_by = request.user
        renewal.review_date = timezone.now()
        renewal.remarks = request.data.get('remarks', 'Renewal rejected by underwriting.')
        renewal.save()

        log_activity(request.user, "Rejected Renewal", "renewals", f"Renewal {renewal.renewal_number} rejected.", request.META.get('REMOTE_ADDR'))
        return Response(RenewalSerializer(renewal).data)
