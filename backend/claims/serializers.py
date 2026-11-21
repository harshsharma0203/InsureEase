from rest_framework import serializers
from .models import Claim, ClaimDocument, ClaimAssessment, ClaimSettlement


class ClaimDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = ClaimDocument
        fields = ['id', 'claim', 'document_name', 'document_type', 'document_type_display', 'document_file', 'file_path', 'file_url', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ClaimAssessmentSerializer(serializers.ModelSerializer):
    assessor_name = serializers.ReadOnlyField(source='assessor.full_name')

    class Meta:
        model = ClaimAssessment
        fields = [
            'id', 'claim', 'assessor', 'assessor_name', 'deductible_amount',
            'co_pay_amount', 'copay_amount', 'admissible_amount', 'final_payable',
            'recommended_settlement', 'assessment_notes',
            'assessed_at'
        ]
        read_only_fields = ['id', 'assessed_at']


class ClaimSettlementSerializer(serializers.ModelSerializer):
    settled_by_name = serializers.ReadOnlyField(source='settled_by.full_name')
    payment_mode_display = serializers.CharField(source='get_payment_mode_display', read_only=True)

    class Meta:
        model = ClaimSettlement
        fields = [
            'id', 'claim', 'settlement_amount', 'settlement_date',
            'bank_transaction_id', 'payment_mode', 'payment_mode_display',
            'bank_name', 'account_number_masked', 'beneficiary_account', 'beneficiary_ifsc',
            'discharged_by', 'status', 'remarks',
            'settled_by', 'settled_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClaimSerializer(serializers.ModelSerializer):
    policy_number = serializers.ReadOnlyField(source='policy.policy_number')
    group_name = serializers.ReadOnlyField(source='policy.group.name')
    member_name = serializers.ReadOnlyField(source='member.full_name')
    member_employee_id = serializers.ReadOnlyField(source='member.employee_id')
    claim_type_display = serializers.CharField(source='get_claim_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    submitted_by_name = serializers.ReadOnlyField(source='submitted_by.full_name')
    assigned_officer_name = serializers.ReadOnlyField(source='assigned_officer.full_name')
    documents = ClaimDocumentSerializer(many=True, read_only=True)
    assessments = ClaimAssessmentSerializer(many=True, read_only=True)
    settlement = ClaimSettlementSerializer(read_only=True)

    class Meta:
        model = Claim
        fields = [
            'id', 'claim_number', 'policy', 'policy_number', 'group_name',
            'member', 'member_name', 'member_employee_id', 'claim_type',
            'claim_type_display', 'incident_date', 'claim_submission_date', 'claim_amount',
            'approved_amount', 'hospital_name', 'diagnosis',
            'incident_description', 'description', 'status', 'claim_status', 'status_display',
            'submitted_by', 'submitted_by_name', 'assigned_officer',
            'assigned_officer_name', 'verification_remarks',
            'rejection_reason', 'settlement_date', 'payment_reference',
            'documents', 'assessments', 'settlement', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'claim_number', 'created_at', 'updated_at']
