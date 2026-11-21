from datetime import date
from decimal import Decimal
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Claim, ClaimDocument, ClaimAssessment, ClaimSettlement, ClaimStatus
from .serializers import (
    ClaimSerializer,
    ClaimDocumentSerializer,
    ClaimAssessmentSerializer,
    ClaimSettlementSerializer
)
from .pdf_utils import generate_claim_settlement_pdf
from policy_management.models import Policy, PolicyStatus, PolicyMember
from accounts.permissions import log_activity
from accounts.models import User


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all().select_related(
        'policy', 'policy__group', 'policy__product', 'member', 'submitted_by', 'assigned_officer'
    ).prefetch_related('documents', 'assessments')
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'claim_number', 'member__first_name', 'member__last_name',
        'member__employee_id', 'policy__policy_number', 'hospital_name', 'diagnosis'
    ]
    ordering_fields = ['id', 'incident_date', 'claim_amount', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(policy__group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(member__user=user)
        elif user.role == 'CLAIMS_OFFICER':
            # Claims officers see claims or their assigned ones
            pass

        policy_id = self.request.query_params.get('policy')
        member_id = self.request.query_params.get('member')
        status_param = self.request.query_params.get('status')
        claim_type = self.request.query_params.get('claim_type')
        if policy_id:
            qs = qs.filter(policy_id=policy_id)
        if member_id:
            qs = qs.filter(member_id=member_id)
        if status_param:
            qs = qs.filter(Q(status__iexact=status_param) | Q(claim_status__iexact=status_param))
        if claim_type:
            qs = qs.filter(claim_type=claim_type)
        return qs

    def perform_create(self, serializer):
        policy = serializer.validated_data.get('policy')
        member = serializer.validated_data.get('member')
        incident_date = serializer.validated_data.get('incident_date')

        # Business Validation
        if policy.status != PolicyStatus.ACTIVE:
            raise serializers.ValidationError({"policy": "Claims can only be filed against an ACTIVE insurance policy."})

        # Verify member enrollment
        enrolled = PolicyMember.objects.filter(policy=policy, member=member, status='ACTIVE').exists()
        if not enrolled:
            raise serializers.ValidationError({"member": "Member is not actively covered under this policy."})

        # Verify date
        if incident_date < policy.start_date or incident_date > policy.expiry_date:
            raise serializers.ValidationError({"incident_date": f"Incident date must fall within policy coverage dates ({policy.start_date} to {policy.expiry_date})."})

        count = Claim.objects.count() + 1
        claim_num = f"CLM-2026-{count:04d}"

        # Assign claims officer if available
        officer = User.objects.filter(role='CLAIMS_OFFICER', is_active=True).first()

        instance = serializer.save(
            claim_number=claim_num,
            submitted_by=self.request.user,
            assigned_officer=officer,
            status=ClaimStatus.SUBMITTED
        )
        log_activity(self.request.user, "Filed Claim", "claims", f"Claim {instance.claim_number} filed for member {member.full_name} under policy {policy.policy_number}.", self.request.META.get('REMOTE_ADDR'))

    @action(detail=True, methods=['post'])
    def assign_officer(self, request, pk=None):
        claim = self.get_object()
        officer_id = request.data.get('officer_id')
        officer = User.objects.filter(id=officer_id, role__in=['CLAIMS_OFFICER', 'INSURANCE_ADMIN', 'SUPER_ADMIN']).first()
        if not officer:
            return Response({"error": "Valid claims officer not found."}, status=status.HTTP_400_BAD_REQUEST)
        claim.assigned_officer = officer
        claim.status = ClaimStatus.UNDER_REVIEW
        claim.save()
        log_activity(request.user, "Assigned Claims Officer", "claims", f"Claim {claim.claim_number} assigned to {officer.full_name}.", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        claim = self.get_object()
        remarks = request.data.get('remarks', 'Eligibility and policy validity verified successfully.')
        req_docs = request.data.get('request_docs', False)

        claim.verification_remarks = remarks
        claim.status = ClaimStatus.DOCUMENTS_REQUIRED if req_docs else ClaimStatus.VERIFIED
        claim.save()

        log_activity(request.user, "Verified Claim", "claims", f"Claim {claim.claim_number} status set to {claim.status}.", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['post'])
    def assess(self, request, pk=None):
        claim = self.get_object()
        deductible = Decimal(str(request.data.get('deductible_amount', '0.00')))
        co_pay = Decimal(str(request.data.get('co_pay_amount', '0.00')))
        notes = request.data.get('assessment_notes', 'Admissibility assessment completed.')
        recommended = Decimal(str(request.data.get('recommended_settlement', claim.claim_amount - deductible - co_pay)))

        assessment = ClaimAssessment.objects.create(
            claim=claim,
            assessor=request.user,
            deductible_amount=deductible,
            co_pay_amount=co_pay,
            recommended_settlement=recommended,
            assessment_notes=notes
        )
        claim.approved_amount = recommended
        claim.status = ClaimStatus.UNDER_REVIEW
        claim.save()

        log_activity(request.user, "Assessed Claim", "claims", f"Claim {claim.claim_number} assessed with recommended amount ₹{recommended}.", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        claim = self.get_object()
        amt = Decimal(str(request.data.get('approved_amount', claim.approved_amount or claim.claim_amount)))
        claim.approved_amount = amt
        claim.status = ClaimStatus.APPROVED
        claim.save()

        log_activity(request.user, "Approved Claim", "claims", f"Claim {claim.claim_number} approved for ₹{amt}.", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        claim = self.get_object()
        reason = request.data.get('rejection_reason', 'Claim rejected under policy exclusions / terms.')
        claim.rejection_reason = reason
        claim.status = ClaimStatus.REJECTED
        claim.save()

        log_activity(request.user, "Rejected Claim", "claims", f"Claim {claim.claim_number} rejected. Reason: {reason}", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        claim = self.get_object()
        if claim.status not in [ClaimStatus.APPROVED, ClaimStatus.SETTLEMENT_PENDING]:
            return Response({"error": "Only approved claims can be settled."}, status=status.HTTP_400_BAD_REQUEST)

        settlement_amt = Decimal(str(request.data.get('settlement_amount', claim.approved_amount)))
        tx_id = request.data.get('bank_transaction_id')
        if not tx_id:
            count = ClaimSettlement.objects.count() + 1
            tx_id = f"UTR-{timezone.now().strftime('%Y%m%d')}-{count:04d}"

        mode = request.data.get('payment_mode', 'NEFT')
        bank = request.data.get('bank_name', 'HDFC Bank')
        acct = request.data.get('account_number_masked', 'XXXX-XXXX-4829')
        remarks = request.data.get('remarks', 'Settlement transfer dispatched.')

        settlement, created = ClaimSettlement.objects.get_or_create(
            claim=claim,
            defaults={
                'settlement_amount': settlement_amt,
                'settlement_date': date.today(),
                'bank_transaction_id': tx_id,
                'payment_mode': mode,
                'bank_name': bank,
                'account_number_masked': acct,
                'status': 'PROCESSED',
                'remarks': remarks,
                'settled_by': request.user
            }
        )

        claim.status = ClaimStatus.SETTLED
        claim.settlement_date = date.today()
        claim.payment_reference = tx_id
        claim.save()

        log_activity(request.user, "Settled Claim", "claims", f"Claim {claim.claim_number} settled for ₹{settlement_amt} with ref {tx_id}.", request.META.get('REMOTE_ADDR'))
        return Response(ClaimSerializer(claim).data)

    @action(detail=True, methods=['get'])
    def download_settlement_letter(self, request, pk=None):
        claim = self.get_object()
        pdf_stream = generate_claim_settlement_pdf(claim)
        response = HttpResponse(pdf_stream.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="InsureEase_Claim_{claim.claim_number}_Settlement.pdf"'
        return response


class ClaimDocumentViewSet(viewsets.ModelViewSet):
    queryset = ClaimDocument.objects.all().select_related('claim')
    serializer_class = ClaimDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "Uploaded Claim Document", "claims", f"Uploaded document {instance.document_name} for claim {instance.claim.claim_number}.", self.request.META.get('REMOTE_ADDR'))


class ClaimAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClaimAssessment.objects.all().select_related('claim', 'assessor')
    serializer_class = ClaimAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClaimSettlementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClaimSettlement.objects.all().select_related('claim', 'settled_by')
    serializer_class = ClaimSettlementSerializer
    permission_classes = [permissions.IsAuthenticated]
