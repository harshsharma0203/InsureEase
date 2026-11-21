from rest_framework import serializers
from .models import Renewal
from policy_management.serializers import PolicySerializer


class RenewalSerializer(serializers.ModelSerializer):
    policy_number = serializers.ReadOnlyField(source='policy.policy_number')
    group_name = serializers.ReadOnlyField(source='policy.group.name')
    product_name = serializers.ReadOnlyField(source='policy.product.name')
    policy_expiry_date = serializers.ReadOnlyField(source='policy.expiry_date')
    renewed_policy_number = serializers.ReadOnlyField(source='renewed_policy.policy_number')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.full_name')

    class Meta:
        model = Renewal
        fields = [
            'id', 'renewal_number', 'policy', 'policy_number', 'group_name',
            'product_name', 'policy_expiry_date', 'previous_expiry_date',
            'previous_annual_premium', 'previous_premium',
            'claims_ratio_percentage', 'revised_premium', 'revised_sum_insured',
            'proposed_start_date', 'proposed_expiry_date', 'reminder_count',
            'last_reminder_sent', 'status', 'renewal_status', 'status_display', 'renewed_policy',
            'renewed_policy_number', 'remarks', 'reviewed_by', 'approved_by', 'reviewed_by_name',
            'review_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'renewal_number', 'previous_annual_premium', 'claims_ratio_percentage',
            'revised_premium', 'revised_sum_insured', 'proposed_start_date',
            'proposed_expiry_date', 'created_at', 'updated_at'
        ]
