from rest_framework import serializers
from .models import (
    InsuranceProduct,
    PolicyApplication,
    UnderwritingRecord,
    Policy,
    PolicyMember,
    PolicyVersion
)
from groups.serializers import InsuranceGroupSerializer
from members.serializers import MemberSerializer


class InsuranceProductSerializer(serializers.ModelSerializer):
    coverage_type_display = serializers.CharField(source='get_coverage_type_display', read_only=True)
    policies_count = serializers.IntegerField(source='policies.count', read_only=True)

    class Meta:
        model = InsuranceProduct
        fields = [
            'id', 'product_code', 'name', 'product_name', 'description', 'coverage_type',
            'insurance_type', 'coverage_type_display', 'min_coverage', 'minimum_coverage',
            'max_coverage', 'maximum_coverage', 'base_rate_percentage', 'base_premium',
            'policy_duration_months', 'eligibility_criteria', 'terms_and_conditions',
            'is_active', 'status', 'policies_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UnderwritingRecordSerializer(serializers.ModelSerializer):
    underwriter_name = serializers.ReadOnlyField(source='underwriter.full_name')
    risk_category_display = serializers.CharField(source='get_risk_category_display', read_only=True)

    class Meta:
        model = UnderwritingRecord
        fields = [
            'id', 'application', 'underwriter', 'underwriter_name',
            'risk_score', 'risk_category', 'risk_category_display',
            'industry_risk_factor', 'group_size_discount',
            'calculated_indicative_premium', 'approved_premium',
            'decision', 'decision_remarks', 'decision_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'policy_number', 'created_at', 'updated_at']


class PolicyApplicationSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source='group.name')
    product_name = serializers.ReadOnlyField(source='product.name')
    applied_by_name = serializers.ReadOnlyField(source='applied_by.full_name')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    underwriting = UnderwritingRecordSerializer(read_only=True)

    class Meta:
        model = PolicyApplication
        fields = [
            'id', 'application_number', 'group', 'group_name', 'product',
            'product_name', 'requested_coverage_per_member', 'requested_coverage',
            'proposed_premium', 'total_members_count',
            'applied_by', 'applied_by_name', 'status', 'application_status', 'status_display',
            'remarks', 'supporting_document', 'underwriting', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'application_number', 'created_at', 'updated_at']


class PolicyMemberSerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')
    member_employee_id = serializers.ReadOnlyField(source='member.employee_id')
    member_department = serializers.ReadOnlyField(source='member.department')

    class Meta:
        model = PolicyMember
        fields = [
            'id', 'policy', 'member', 'member_name', 'member_employee_id',
            'member_department', 'coverage_amount', 'individual_premium',
            'effective_date', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PolicyVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = PolicyVersion
        fields = [
            'id', 'policy', 'version_number', 'snapshot_data',
            'change_reason', 'effective_date', 'created_by',
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PolicySerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source='group.name')
    product_name = serializers.ReadOnlyField(source='product.name')
    coverage_type = serializers.ReadOnlyField(source='product.coverage_type')
    coverage_type_display = serializers.CharField(source='product.get_coverage_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    members_count = serializers.IntegerField(source='policy_members.count', read_only=True)
    versions_count = serializers.IntegerField(source='versions.count', read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'policy_number', 'application', 'group', 'group_name',
            'product', 'product_name', 'coverage_type', 'coverage_type_display',
            'sum_insured_per_member', 'total_members_covered', 'total_sum_insured',
            'coverage_amount', 'base_annual_premium', 'tax_amount', 'total_premium',
            'annual_premium', 'start_date', 'expiry_date', 'status', 'policy_status',
            'status_display', 'issued_by',
            'terms_and_conditions', 'policy_pdf', 'members_count', 'versions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'policy_number', 'created_at', 'updated_at']
