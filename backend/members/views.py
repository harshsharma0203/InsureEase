from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Member
from .serializers import MemberSerializer
from accounts.permissions import log_activity


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all().select_related('group', 'user').prefetch_related('policy_enrollments')
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'employee_id', 'member_code', 'email', 'phone', 'group__name']
    ordering_fields = ['id', 'first_name', 'date_of_joining', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(user=user)

        group_id = self.request.query_params.get('group')
        status_param = self.request.query_params.get('status')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        member_code = self.request.data.get('member_code')
        if not member_code:
            count = Member.objects.count() + 1
            member_code = f"MEM-2026-{count:05d}"
        instance = serializer.save(member_code=member_code)
        log_activity(self.request.user, "Enrolled Member", "members", f"Member {instance.full_name} enrolled into {instance.group.name}.", self.request.META.get('REMOTE_ADDR'))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "Updated Member", "members", f"Member {instance.full_name} profile updated.", self.request.META.get('REMOTE_ADDR'))
