from rest_framework import serializers
from .models import Endorsement
from policy_management.serializers import PolicySerializer
from members.serializers import MemberSerializer


class EndorsementSerializer(serializers.ModelSerializer):
    policy_number = serializers.ReadOnlyField(source='policy.policy_number')
    group_name = serializers.ReadOnlyField(source='policy.group.name')
    member_name = serializers.ReadOnlyField(source='member.full_name')
    endorsement_type_display = serializers.CharField(source='get_endorsement_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by_name = serializers.ReadOnlyField(source='requested_by.full_name')
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.full_name')

    class Meta:
        model = Endorsement
        fields = [
            'id', 'endorsement_number', 'policy', 'policy_number', 'group_name',
            'endorsement_type', 'endorsement_type_display', 'member', 'member_name',
            'requested_by', 'requested_by_name', 'reason', 'effective_date',
            'changes_data', 'old_value', 'new_value', 'premium_adjustment', 'status', 'status_display',
            'reviewed_by', 'reviewed_by_name', 'review_notes', 'review_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'endorsement_number', 'created_at', 'updated_at']
