from rest_framework import serializers
from django.db.models import Q
from .models import InsuranceGroup
from accounts.serializers import UserSerializer


class InsuranceGroupSerializer(serializers.ModelSerializer):
    manager_name = serializers.ReadOnlyField(source='manager.full_name')
    members_count = serializers.IntegerField(source='members.count', read_only=True)
    active_policies_count = serializers.SerializerMethodField()

    class Meta:
        model = InsuranceGroup
        fields = [
            'id', 'group_code', 'name', 'group_name', 'organization_name',
            'registration_number', 'industry', 'industry_type',
            'contact_person', 'contact_email', 'contact_phone', 'address',
            'city', 'state', 'pincode', 'postal_code', 'manager', 'group_manager',
            'manager_name', 'employee_count', 'total_employees', 'members_count',
            'active_policies_count', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'group_code', 'created_at', 'updated_at']

    def get_active_policies_count(self, obj):
        return obj.policies.filter(Q(status__iexact='ACTIVE') | Q(policy_status__iexact='ACTIVE')).count()
