from datetime import date
from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Agent, Commission, CommissionStatus
from .serializers import AgentSerializer, CommissionSerializer
from accounts.permissions import log_activity


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all().prefetch_related('commissions')
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'agent_code', 'agency_name', 'license_number', 'email', 'phone']
    ordering_fields = ['id', 'name', 'total_earned', 'created_at']
    ordering = ['-id']

    def perform_create(self, serializer):
        count = Agent.objects.count() + 1
        agent_code = f"AGT-2026-{count:04d}"
        instance = serializer.save(agent_code=agent_code)
        log_activity(self.request.user, "Registered Agent", "commissions", f"Agent {instance.name} ({instance.agent_code}) registered.", self.request.META.get('REMOTE_ADDR'))


class CommissionViewSet(viewsets.ModelViewSet):
    queryset = Commission.objects.all().select_related('agent', 'policy', 'policy__group', 'invoice', 'approved_by')
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['commission_number', 'agent__name', 'agent__agent_code', 'policy__policy_number', 'invoice__invoice_number']
    ordering_fields = ['id', 'commission_amount', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        qs = super().get_queryset()
        agent_id = self.request.query_params.get('agent')
        status_param = self.request.query_params.get('status')
        if agent_id:
            qs = qs.filter(agent_id=agent_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        comm = self.get_object()
        comm.status = CommissionStatus.APPROVED
        comm.approved_by = request.user
        comm.remarks = request.data.get('remarks', 'Commission validated and approved for payout.')
        comm.save()
        log_activity(request.user, "Approved Commission", "commissions", f"Commission {comm.commission_number} approved.", request.META.get('REMOTE_ADDR'))
        return Response(CommissionSerializer(comm).data)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        comm = self.get_object()
        tx_ref = request.data.get('payment_reference')
        if not tx_ref:
            count = Commission.objects.filter(status='PAID').count() + 1
            tx_ref = f"COMM-DISB-{date.today().strftime('%Y%m')}-{count:04d}"

        comm.status = CommissionStatus.PAID
        comm.payment_date = date.today()
        comm.payment_reference = tx_ref
        comm.remarks = request.data.get('remarks', 'Commission disbursement completed.')
        comm.save()

        # Update Agent paid accumulator
        comm.agent.total_paid += comm.commission_amount
        comm.agent.save()

        log_activity(request.user, "Disbursed Commission", "commissions", f"Commission {comm.commission_number} marked paid with ref {tx_ref}.", request.META.get('REMOTE_ADDR'))
        return Response(CommissionSerializer(comm).data)

    @action(detail=False, methods=['get'])
    def reports(self, request):
        """Returns agent-wise commission analytics and summary metrics."""
        agents = Agent.objects.all().annotate(
            total_commissions_count=Count('commissions'),
            pending_amount=Sum('commissions__commission_amount', filter=models.Q(commissions__status='PENDING')),
            paid_amount=Sum('commissions__commission_amount', filter=models.Q(commissions__status='PAID'))
        )
        report_data = []
        for ag in agents:
            report_data.append({
                'agent_id': ag.id,
                'agent_code': ag.agent_code,
                'agent_name': ag.name,
                'agency_name': ag.agency_name,
                'commission_rate': ag.default_commission_rate,
                'total_commissions_count': ag.total_commissions_count,
                'total_earned': ag.total_earned,
                'total_paid': ag.total_paid,
                'pending_amount': ag.pending_amount or Decimal('0.00'),
            })

        overall_total = Commission.objects.aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        overall_pending = Commission.objects.filter(status='PENDING').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        overall_paid = Commission.objects.filter(status='PAID').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')

        return Response({
            'overall_summary': {
                'total_commission_generated': overall_total,
                'pending_commissions': overall_pending,
                'paid_commissions': overall_paid,
            },
            'agent_reports': report_data
        })
