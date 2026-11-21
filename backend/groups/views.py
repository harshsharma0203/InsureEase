import uuid
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from .models import InsuranceGroup
from .serializers import InsuranceGroupSerializer
from accounts.permissions import log_activity


class InsuranceGroupViewSet(viewsets.ModelViewSet):
    queryset = InsuranceGroup.objects.all().select_related('manager').prefetch_related('members', 'policies')
    serializer_class = InsuranceGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'group_code', 'registration_number', 'industry', 'city', 'contact_person']
    ordering_fields = ['id', 'name', 'employee_count', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        # Group Managers only see their own group
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(manager=user)
        # Policyholder sees their enrolled group
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(members__user=user).distinct()

        industry = self.request.query_params.get('industry')
        status = self.request.query_params.get('status')
        if industry:
            qs = qs.filter(industry=industry)
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        # Auto-generate group_code if not provided
        group_code = self.request.data.get('group_code')
        if not group_code:
            count = InsuranceGroup.objects.count() + 1
            group_code = f"GRP-2026-{count:04d}"
        instance = serializer.save(group_code=group_code)
        log_activity(self.request.user, "Created Insurance Group", "groups", f"Group {instance.name} ({instance.group_code}) registered.", self.request.META.get('REMOTE_ADDR'))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "Updated Insurance Group", "groups", f"Group {instance.name} updated.", self.request.META.get('REMOTE_ADDR'))
