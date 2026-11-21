from rest_framework import serializers
from .models import Member
from groups.models import InsuranceGroup


class MemberSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source='group.name')
    full_name = serializers.ReadOnlyField()
    active_coverage = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id', 'member_code', 'group', 'group_name', 'user',
            'first_name', 'last_name', 'full_name', 'date_of_birth',
            'gender', 'email', 'phone', 'phone_number', 'employee_id', 'designation',
            'department', 'date_of_joining', 'address', 'nominee_name',
            'nominee_relationship', 'nominee_phone', 'status', 'member_status',
            'active_coverage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'member_code', 'created_at', 'updated_at']

    def get_active_coverage(self, obj):
        active_enrollment = obj.policy_enrollments.filter(status='ACTIVE').first()
        if active_enrollment:
            return {
                'policy_number': active_enrollment.policy.policy_number,
                'product_name': active_enrollment.policy.product.name,
                'coverage_amount': active_enrollment.coverage_amount,
                'effective_date': active_enrollment.effective_date,
            }
        return None
