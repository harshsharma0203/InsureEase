from datetime import date, timedelta
from decimal import Decimal
import json

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    InsuranceProduct,
    PolicyApplication,
    UnderwritingRecord,
    Policy,
    PolicyMember,
    PolicyVersion,
    ApplicationStatus,
    PolicyStatus,
    RiskCategory
)
from .serializers import (
    InsuranceProductSerializer,
    PolicyApplicationSerializer,
    UnderwritingRecordSerializer,
    PolicySerializer,
    PolicyMemberSerializer,
    PolicyVersionSerializer
)
from .pdf_utils import generate_policy_pdf_stream
from accounts.permissions import log_activity
from members.models import Member


def calculate_risk_and_premium(group, product, requested_coverage_per_member, total_members):
    """
    Transparent, configurable business rules for underwriting risk score and indicative premium.
    Scale: 0 - 100
    """
    base_score = Decimal('30.00')

    # 1. Industry factor
    ind = (group.industry or '').lower()
    if any(k in ind for k in ['it', 'software', 'technology', 'education', 'banking', 'finance']):
        industry_risk_factor = Decimal('0.90')
        ind_adj = Decimal('-5.00')
    elif any(k in ind for k in ['manufacturing', 'logistics', 'transport', 'hospitality']):
        industry_risk_factor = Decimal('1.15')
        ind_adj = Decimal('10.00')
    elif any(k in ind for k in ['mining', 'construction', 'chemical', 'oil']):
        industry_risk_factor = Decimal('1.40')
        ind_adj = Decimal('25.00')
    else:
        industry_risk_factor = Decimal('1.00')
        ind_adj = Decimal('0.00')

    # 2. Group size discount
    size = int(total_members)
    if size >= 500:
        group_size_discount = Decimal('0.20')
        size_adj = Decimal('-15.00')
    elif size >= 200:
        group_size_discount = Decimal('0.15')
        size_adj = Decimal('-10.00')
    elif size >= 50:
        group_size_discount = Decimal('0.10')
        size_adj = Decimal('-5.00')
    elif size >= 20:
        group_size_discount = Decimal('0.05')
        size_adj = Decimal('0.00')
    else:
        group_size_discount = Decimal('0.00')
        size_adj = Decimal('10.00')

    # Final risk score
    raw_score = base_score + ind_adj + size_adj
    risk_score = max(Decimal('10.00'), min(Decimal('95.00'), raw_score))

    if risk_score < 35:
        risk_category = RiskCategory.LOW
    elif risk_score <= 55:
        risk_category = RiskCategory.MEDIUM
    elif risk_score <= 75:
        risk_category = RiskCategory.HIGH
    else:
        risk_category = RiskCategory.VERY_HIGH

    # Premium calculation
    total_coverage = Decimal(str(requested_coverage_per_member)) * Decimal(str(total_members))
    base_rate = product.base_rate_percentage
    # Risk adjusted rate = base_rate * (risk_score / 35.0) * (1 - group_size_discount)
    risk_multiplier = (risk_score / Decimal('35.00')) * (Decimal('1.00') - group_size_discount)
    effective_rate = (base_rate * risk_multiplier).quantize(Decimal('0.01'))
    indicative_premium = (total_coverage * (effective_rate / Decimal('100.00'))).quantize(Decimal('0.01'))

    return {
        'risk_score': risk_score,
        'risk_category': risk_category,
        'industry_risk_factor': industry_risk_factor,
        'group_size_discount': group_size_discount,
        'effective_rate_percentage': effective_rate,
        'indicative_premium': indicative_premium,
        'total_coverage': total_coverage
    }


class InsuranceProductViewSet(viewsets.ModelViewSet):
    queryset = InsuranceProduct.objects.all().prefetch_related('policies')
    serializer_class = InsuranceProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'product_code', 'description', 'coverage_type']
    ordering_fields = ['id', 'name', 'base_rate_percentage', 'created_at']
    ordering = ['-id']

    def perform_create(self, serializer):
        code = self.request.data.get('product_code')
        if not code:
            count = InsuranceProduct.objects.count() + 1
            code = f"PROD-G{count:03d}"
        instance = serializer.save(product_code=code)
        log_activity(self.request.user, "Created Insurance Product", "policy_management", f"Product {instance.name} created.", self.request.META.get('REMOTE_ADDR'))


class PolicyApplicationViewSet(viewsets.ModelViewSet):
    queryset = PolicyApplication.objects.all().select_related('group', 'product', 'applied_by', 'underwriting')
    serializer_class = PolicyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['application_number', 'group__name', 'product__name', 'status']
    ordering_fields = ['id', 'created_at', 'status']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(group__members__user=user).distinct()

        group_id = self.request.query_params.get('group')
        status_param = self.request.query_params.get('status')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if status_param:
            qs = qs.filter(Q(status__iexact=status_param) | Q(policy_status__iexact=status_param))
        return qs

    def perform_create(self, serializer):
        count = PolicyApplication.objects.count() + 1
        app_num = f"APP-2026-{count:04d}"
        app = serializer.save(
            application_number=app_num,
            applied_by=self.request.user,
            status=ApplicationStatus.SUBMITTED
        )

        # Automatically compute transparent underwriting record
        calc = calculate_risk_and_premium(
            group=app.group,
            product=app.product,
            requested_coverage_per_member=app.requested_coverage_per_member,
            total_members=app.total_members_count
        )
        UnderwritingRecord.objects.create(
            application=app,
            risk_score=calc['risk_score'],
            risk_category=calc['risk_category'],
            industry_risk_factor=calc['industry_risk_factor'],
            group_size_discount=calc['group_size_discount'],
            calculated_indicative_premium=calc['indicative_premium'],
            approved_premium=calc['indicative_premium'],
            decision='PENDING'
        )

        log_activity(self.request.user, "Submitted Policy Application", "policy_management", f"Application {app.application_number} submitted for {app.group.name}.", self.request.META.get('REMOTE_ADDR'))

    @action(detail=True, methods=['post'])
    def recalculate_risk(self, request, pk=None):
        app = self.get_object()
        calc = calculate_risk_and_premium(
            group=app.group,
            product=app.product,
            requested_coverage_per_member=app.requested_coverage_per_member,
            total_members=app.total_members_count
        )
        uw, _ = UnderwritingRecord.objects.get_or_create(application=app)
        uw.risk_score = calc['risk_score']
        uw.risk_category = calc['risk_category']
        uw.industry_risk_factor = calc['industry_risk_factor']
        uw.group_size_discount = calc['group_size_discount']
        uw.calculated_indicative_premium = calc['indicative_premium']
        uw.save()
        return Response(UnderwritingRecordSerializer(uw).data)


class UnderwritingViewSet(viewsets.ModelViewSet):
    queryset = UnderwritingRecord.objects.all().select_related('application', 'underwriter', 'application__group', 'application__product')
    serializer_class = UnderwritingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        uw = self.get_object()
        app = uw.application

        remarks = request.data.get('remarks', 'Underwriting evaluation completed and approved.')
        approved_premium = Decimal(str(request.data.get('approved_premium', uw.calculated_indicative_premium)))

        uw.decision = 'APPROVED'
        uw.underwriter = request.user
        uw.approved_premium = approved_premium
        uw.decision_remarks = remarks
        uw.decision_date = timezone.now()
        uw.save()

        app.status = ApplicationStatus.APPROVED
        app.save()

        # Generate Issued Policy!
        count = Policy.objects.count() + 1
        policy_num = f"POL-2026-{count:04d}"
        start_date = date.today()
        expiry_date = start_date + timedelta(days=app.product.policy_duration_months * 30)

        tax = (approved_premium * Decimal('0.18')).quantize(Decimal('0.01'))
        total_premium = approved_premium + tax

        policy = Policy.objects.create(
            policy_number=policy_num,
            application=app,
            group=app.group,
            product=app.product,
            sum_insured_per_member=app.requested_coverage_per_member,
            total_members_covered=app.total_members_count,
            total_sum_insured=app.requested_coverage_per_member * app.total_members_count,
            base_annual_premium=approved_premium,
            tax_amount=tax,
            total_premium=total_premium,
            start_date=start_date,
            expiry_date=expiry_date,
            status=PolicyStatus.ACTIVE
        )

        app.status = ApplicationStatus.ISSUED
        app.save()

        # Enroll all existing members of the group
        members = Member.objects.filter(group=app.group, status='ACTIVE')
        for m in members:
            PolicyMember.objects.get_or_create(
                policy=policy,
                member=m,
                defaults={
                    'coverage_amount': app.requested_coverage_per_member,
                    'individual_premium': (approved_premium / max(1, app.total_members_count)).quantize(Decimal('0.01')),
                    'effective_date': start_date,
                    'status': 'ACTIVE'
                }
            )

        # Policy Version 1 Snapshot
        PolicyVersion.objects.create(
            policy=policy,
            version_number=1,
            snapshot_data={
                'policy_number': policy.policy_number,
                'group': policy.group.name,
                'product': policy.product.name,
                'sum_insured_per_member': str(policy.sum_insured_per_member),
                'total_members_covered': policy.total_members_covered,
                'total_premium': str(policy.total_premium),
                'start_date': str(policy.start_date),
                'expiry_date': str(policy.expiry_date),
            },
            change_reason="Initial Policy Issuance upon Underwriting Approval",
            effective_date=start_date,
            created_by=request.user
        )

        # Automatically Generate Initial Billing Invoice!
        from billing.models import Invoice
        inv_count = Invoice.objects.count() + 1
        Invoice.objects.create(
            invoice_number=f"INV-2026-{inv_count:04d}",
            policy=policy,
            group=policy.group,
            invoice_date=start_date,
            due_date=start_date + timedelta(days=30),
            subtotal_amount=approved_premium,
            tax_rate_percentage=Decimal('18.00'),
            tax_amount=tax,
            total_amount=total_premium,
            paid_amount=Decimal('0.00'),
            balance_due=total_premium,
            status='UNPAID',
            notes=f"Initial annual premium invoice for policy {policy.policy_number}"
        )

        log_activity(request.user, "Approved Underwriting & Issued Policy", "policy_management", f"Policy {policy.policy_number} issued for {policy.group.name}.", request.META.get('REMOTE_ADDR'))
        return Response({
            "detail": "Underwriting approved and Policy successfully issued.",
            "policy": PolicySerializer(policy).data,
            "underwriting": UnderwritingRecordSerializer(uw).data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        uw = self.get_object()
        remarks = request.data.get('remarks', 'Application does not meet group underwriting risk guidelines.')
        uw.decision = 'REJECTED'
        uw.underwriter = request.user
        uw.decision_remarks = remarks
        uw.decision_date = timezone.now()
        uw.save()

        app = uw.application
        app.status = ApplicationStatus.REJECTED
        app.remarks = remarks
        app.save()

        log_activity(request.user, "Rejected Underwriting Application", "policy_management", f"Underwriting rejected for {app.application_number}.", request.META.get('REMOTE_ADDR'))
        return Response(UnderwritingRecordSerializer(uw).data)

    @action(detail=True, methods=['post'])
    def request_info(self, request, pk=None):
        uw = self.get_object()
        remarks = request.data.get('remarks', 'Please upload additional census & historical claims data.')
        uw.decision = 'INFO_REQUESTED'
        uw.decision_remarks = remarks
        uw.save()

        app = uw.application
        app.status = ApplicationStatus.ADDITIONAL_INFO_REQUIRED
        app.remarks = remarks
        app.save()

        log_activity(request.user, "Requested Additional Information", "policy_management", f"Additional information requested for {app.application_number}.", request.META.get('REMOTE_ADDR'))
        return Response(UnderwritingRecordSerializer(uw).data)


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all().select_related('group', 'product', 'application').prefetch_related('policy_members', 'versions')
    serializer_class = PolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['policy_number', 'group__name', 'product__name', 'status']
    ordering_fields = ['id', 'start_date', 'expiry_date', 'total_premium']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(policy_members__member__user=user).distinct()

        group_id = self.request.query_params.get('group')
        product_id = self.request.query_params.get('product')
        status_param = self.request.query_params.get('status')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        if status_param:
            qs = qs.filter(Q(status__iexact=status_param) | Q(policy_status__iexact=status_param))
        return qs

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        policy = self.get_object()
        pdf_stream = generate_policy_pdf_stream(policy)
        response = HttpResponse(pdf_stream.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="InsureEase_Policy_{policy.policy_number}.pdf"'
        return response

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        policy = self.get_object()
        versions = policy.versions.all().order_by('-version_number')
        serializer = PolicyVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        policy = self.get_object()
        members = policy.policy_members.all().select_related('member')
        serializer = PolicyMemberSerializer(members, many=True)
        return Response(serializer.data)


class PolicyMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PolicyMember.objects.all().select_related('policy', 'member')
    serializer_class = PolicyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]


class PolicyVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PolicyVersion.objects.all().select_related('policy', 'created_by')
    serializer_class = PolicyVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
