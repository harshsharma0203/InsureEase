from rest_framework import serializers
from .models import Agent, Commission


class AgentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    commissions_count = serializers.IntegerField(source='commissions.count', read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'agent_code', 'user', 'name', 'email', 'phone', 'contact_number',
            'agency_name', 'license_number', 'default_commission_rate', 'commission_rate',
            'total_earned', 'total_paid', 'status', 'status_display',
            'bank_account_number', 'bank_ifsc', 'commissions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'agent_code', 'created_at', 'updated_at']


class CommissionSerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.name')
    agent_code = serializers.ReadOnlyField(source='agent.agent_code')
    agency_name = serializers.ReadOnlyField(source='agent.agency_name')
    policy_number = serializers.ReadOnlyField(source='policy.policy_number')
    group_name = serializers.ReadOnlyField(source='policy.group.name')
    invoice_number = serializers.ReadOnlyField(source='invoice.invoice_number')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.ReadOnlyField(source='approved_by.full_name')

    class Meta:
        model = Commission
        fields = [
            'id', 'commission_number', 'agent', 'agent_name', 'agent_code',
            'agency_name', 'policy', 'policy_number', 'group_name',
            'invoice', 'invoice_number', 'eligible_premium_amount', 'eligible_premium',
            'rate_percentage', 'commission_rate', 'commission_amount', 'status',
            'commission_status', 'status_display',
            'payment_date', 'paid_date', 'payment_reference', 'approved_by',
            'approved_by_name', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'commission_number', 'rate_percentage', 'commission_amount', 'created_at', 'updated_at']
