from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Endorsement, EndorsementStatus
from .serializers import EndorsementSerializer
from policy_management.models import Policy, PolicyMember, PolicyVersion
from accounts.permissions import log_activity
from billing.models import Invoice


class EndorsementViewSet(viewsets.ModelViewSet):
    queryset = Endorsement.objects.all().select_related('policy', 'policy__group', 'member', 'requested_by', 'reviewed_by')
    serializer_class = EndorsementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['endorsement_number', 'policy__policy_number', 'policy__group__name', 'member__first_name', 'member__last_name', 'reason']
    ordering_fields = ['id', 'created_at', 'effective_date', 'premium_adjustment']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(policy__group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(member__user=user)

        policy_id = self.request.query_params.get('policy')
        status_param = self.request.query_params.get('status')
        etype = self.request.query_params.get('type')
        if policy_id:
            qs = qs.filter(policy_id=policy_id)
        if status_param:
            qs = qs.filter(status=status_param)
        if etype:
            qs = qs.filter(endorsement_type=etype)
        return qs

    def perform_create(self, serializer):
        count = Endorsement.objects.count() + 1
        endorsement_number = f"END-2026-{count:04d}"
        policy = serializer.validated_data.get('policy')
        changes_data = self.request.data.get('changes_data', {})
        premium_adj = Decimal(str(self.request.data.get('premium_adjustment', '0.00')))

        # If adding member and premium adjustment not specified, calculate prorated member premium
        etype = serializer.validated_data.get('endorsement_type')
        if etype == 'ADD_MEMBER' and premium_adj == Decimal('0.00') and policy:
            # Prorated calculation based on remaining days
            days_remaining = max(1, (policy.expiry_date - date.today()).days)
            annual_per_member = policy.base_annual_premium / max(1, policy.total_members_covered)
            premium_adj = (annual_per_member * Decimal(str(days_remaining)) / Decimal('365.00')).quantize(Decimal('0.01'))

        instance = serializer.save(
            endorsement_number=endorsement_number,
            requested_by=self.request.user,
            premium_adjustment=premium_adj,
            changes_data=changes_data,
            status=EndorsementStatus.PENDING
        )
        log_activity(self.request.user, "Created Endorsement Request", "endorsements", f"Endorsement {instance.endorsement_number} for Policy {policy.policy_number} submitted.", self.request.META.get('REMOTE_ADDR'))

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        endorsement = self.get_object()
        if endorsement.status != EndorsementStatus.PENDING:
            return Response({"error": "Only pending endorsements can be approved."}, status=status.HTTP_400_BAD_REQUEST)

        policy = endorsement.policy
        notes = request.data.get('review_notes', 'Endorsement approved and applied to policy.')
        endorsement.status = EndorsementStatus.APPROVED
        endorsement.reviewed_by = request.user
        endorsement.review_notes = notes
        endorsement.review_date = timezone.now()
        endorsement.save()

        # Apply endorsement changes while preserving version history
        next_ver = policy.versions.count() + 1

        if endorsement.endorsement_type == 'ADD_MEMBER' and endorsement.member:
            pm, created = PolicyMember.objects.get_or_create(
                policy=policy,
                member=endorsement.member,
                defaults={
                    'coverage_amount': policy.sum_insured_per_member,
                    'individual_premium': endorsement.premium_adjustment,
                    'effective_date': endorsement.effective_date,
                    'status': 'ACTIVE'
                }
            )
            policy.total_members_covered += 1
            policy.total_sum_insured += policy.sum_insured_per_member
            policy.total_premium += endorsement.premium_adjustment
            policy.save()

        elif endorsement.endorsement_type == 'REMOVE_MEMBER' and endorsement.member:
            pm = PolicyMember.objects.filter(policy=policy, member=endorsement.member).first()
            if pm:
                pm.status = 'ENDORSED_OUT'
                pm.save()
                policy.total_members_covered = max(1, policy.total_members_covered - 1)
                policy.total_sum_insured = max(Decimal('0.00'), policy.total_sum_insured - policy.sum_insured_per_member)
                policy.save()

        elif endorsement.endorsement_type == 'CHANGE_COVERAGE':
            new_cov = endorsement.changes_data.get('new_coverage')
            if new_cov:
                policy.sum_insured_per_member = Decimal(str(new_cov))
                policy.total_sum_insured = policy.sum_insured_per_member * policy.total_members_covered
                policy.save()

        # Audit Version History snapshot
        PolicyVersion.objects.create(
            policy=policy,
            version_number=next_ver,
            snapshot_data={
                'policy_number': policy.policy_number,
                'total_members_covered': policy.total_members_covered,
                'total_sum_insured': str(policy.total_sum_insured),
                'total_premium': str(policy.total_premium),
                'endorsement_number': endorsement.endorsement_number,
                'endorsement_type': endorsement.endorsement_type,
                'premium_adjustment': str(endorsement.premium_adjustment),
                'reason': endorsement.reason,
            },
            change_reason=f"Endorsement {endorsement.endorsement_number}: {endorsement.get_endorsement_type_display()}",
            effective_date=endorsement.effective_date,
            created_by=request.user
        )

        # If additional premium adjustment > 0, generate endorsement invoice
        if endorsement.premium_adjustment > Decimal('0.00'):
            inv_count = Invoice.objects.count() + 1
            tax = (endorsement.premium_adjustment * Decimal('0.18')).quantize(Decimal('0.01'))
            tot = endorsement.premium_adjustment + tax
            Invoice.objects.create(
                invoice_number=f"INV-2026-{inv_count:04d}",
                policy=policy,
                group=policy.group,
                invoice_date=date.today(),
                due_date=date.today() + timedelta(days=15),
                subtotal_amount=endorsement.premium_adjustment,
                tax_rate_percentage=Decimal('18.00'),
                tax_amount=tax,
                total_amount=tot,
                paid_amount=Decimal('0.00'),
                balance_due=tot,
                status='UNPAID',
                notes=f"Endorsement adjustment invoice for {endorsement.endorsement_number}"
            )

        endorsement.status = EndorsementStatus.COMPLETED
        endorsement.save()

        log_activity(request.user, "Approved Endorsement", "endorsements", f"Endorsement {endorsement.endorsement_number} approved and Policy version {next_ver} created.", request.META.get('REMOTE_ADDR'))
        return Response(EndorsementSerializer(endorsement).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        endorsement = self.get_object()
        notes = request.data.get('review_notes', 'Endorsement rejected.')
        endorsement.status = EndorsementStatus.REJECTED
        endorsement.reviewed_by = request.user
        endorsement.review_notes = notes
        endorsement.review_date = timezone.now()
        endorsement.save()

        log_activity(request.user, "Rejected Endorsement", "endorsements", f"Endorsement {endorsement.endorsement_number} rejected.", request.META.get('REMOTE_ADDR'))
        return Response(EndorsementSerializer(endorsement).data)
