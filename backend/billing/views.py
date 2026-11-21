from datetime import date
from decimal import Decimal
from django.http import HttpResponse
from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Invoice, Payment, InvoiceStatus
from .serializers import InvoiceSerializer, PaymentSerializer
from .pdf_utils import generate_invoice_pdf
from accounts.permissions import log_activity
from commissions.models import Agent, Commission, CommissionStatus


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().select_related('policy', 'policy__product', 'group').prefetch_related('payments')
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'group__name', 'policy__policy_number']
    ordering_fields = ['id', 'invoice_date', 'due_date', 'total_amount', 'balance_due']
    ordering = ['-invoice_date']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(group__members__user=user).distinct()

        policy_id = self.request.query_params.get('policy')
        group_id = self.request.query_params.get('group')
        status_param = self.request.query_params.get('status')
        if policy_id:
            qs = qs.filter(policy_id=policy_id)
        if group_id:
            qs = qs.filter(group_id=group_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        invoice = self.get_object()
        amount = Decimal(str(request.data.get('amount', invoice.balance_due)))
        method = request.data.get('payment_method', 'NEFT')
        tx_id = request.data.get('transaction_id')
        payer = request.data.get('payer_name', invoice.group.name)
        notes = request.data.get('notes', 'Payment received and credited.')

        if amount <= Decimal('0.00'):
            return Response({"error": "Payment amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        if amount > invoice.balance_due:
            return Response({"error": f"Payment amount (₹{amount}) cannot exceed outstanding balance due (₹{invoice.balance_due})."}, status=status.HTTP_400_BAD_REQUEST)

        if not tx_id:
            count = Payment.objects.count() + 1
            tx_id = f"TXN-{date.today().strftime('%Y%m%d')}-{count:05d}"

        # Prevent duplicate payment transaction_id
        if Payment.objects.filter(transaction_id=tx_id).exists():
            return Response({"error": "A payment with this transaction ID has already been recorded."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pay_count = Payment.objects.count() + 1
            receipt_num = f"RCP-2026-{pay_count:05d}"
            ref_num = f"PAY-2026-{pay_count:05d}"

            payment = Payment.objects.create(
                payment_reference=ref_num,
                invoice=invoice,
                payment_date=date.today(),
                amount=amount,
                payment_method=method,
                transaction_id=tx_id,
                payer_name=payer,
                receipt_number=receipt_num,
                status='SUCCESS',
                notes=notes,
                recorded_by=request.user
            )

            invoice.paid_amount += amount
            invoice.balance_due -= amount
            if invoice.balance_due <= Decimal('0.00'):
                invoice.status = InvoiceStatus.PAID
                invoice.balance_due = Decimal('0.00')
            else:
                invoice.status = InvoiceStatus.PARTIALLY_PAID
            invoice.save()

            # Automatic Commission Calculation for eligible Agent
            agent = Agent.objects.filter(status='ACTIVE').order_by('id').first()
            if agent:
                # Calculate base eligible premium (excluding GST)
                eligible_ratio = invoice.subtotal_amount / max(Decimal('1.00'), invoice.total_amount)
                eligible_premium = (amount * eligible_ratio).quantize(Decimal('0.01'))
                rate = agent.default_commission_rate
                comm_amt = (eligible_premium * (rate / Decimal('100.00'))).quantize(Decimal('0.01'))

                comm_count = Commission.objects.count() + 1
                comm_num = f"COM-2026-{comm_count:04d}"

                # Avoid duplicate commission for same agent, policy, invoice
                if not Commission.objects.filter(agent=agent, policy=invoice.policy, invoice=invoice).exists():
                    Commission.objects.create(
                        commission_number=comm_num,
                        agent=agent,
                        policy=invoice.policy,
                        invoice=invoice,
                        eligible_premium_amount=eligible_premium,
                        rate_percentage=rate,
                        commission_amount=comm_amt,
                        status=CommissionStatus.PENDING,
                        remarks=f"Generated from Invoice payment {receipt_num}"
                    )
                    agent.total_earned += comm_amt
                    agent.save()

        log_activity(request.user, "Recorded Payment", "billing", f"Payment ₹{amount} recorded for Invoice {invoice.invoice_number} (Receipt {receipt_num}).", request.META.get('REMOTE_ADDR'))
        return Response({
            "detail": "Payment recorded successfully.",
            "payment": PaymentSerializer(payment).data,
            "invoice": InvoiceSerializer(invoice).data
        })

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()
        pdf_stream = generate_invoice_pdf(invoice)
        response = HttpResponse(pdf_stream.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="InsureEase_Invoice_{invoice.invoice_number}.pdf"'
        return response


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all().select_related('invoice', 'invoice__group', 'recorded_by')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['payment_reference', 'transaction_id', 'receipt_number', 'payer_name', 'invoice__invoice_number']
    ordering_fields = ['id', 'payment_date', 'amount', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'GROUP_MANAGER':
            qs = qs.filter(invoice__group__manager=user)
        elif user.role == 'POLICYHOLDER':
            qs = qs.filter(invoice__group__members__user=user).distinct()
        return qs
