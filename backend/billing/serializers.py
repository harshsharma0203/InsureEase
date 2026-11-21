from rest_framework import serializers
from .models import Invoice, Payment


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.ReadOnlyField(source='invoice.invoice_number')
    group_name = serializers.ReadOnlyField(source='invoice.group.name')
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    recorded_by_name = serializers.ReadOnlyField(source='recorded_by.full_name')

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_reference', 'transaction_reference', 'invoice', 'invoice_number', 'group_name',
            'payment_date', 'amount', 'payment_amount', 'payment_method', 'payment_method_display',
            'transaction_id', 'payer_name', 'receipt_number', 'status', 'payment_status',
            'notes', 'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'payment_reference', 'receipt_number', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    policy_number = serializers.ReadOnlyField(source='policy.policy_number')
    group_name = serializers.ReadOnlyField(source='group.name')
    product_name = serializers.ReadOnlyField(source='policy.product.name')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'policy', 'policy_number', 'group',
            'group_name', 'product_name', 'invoice_date', 'due_date',
            'subtotal_amount', 'subtotal', 'tax_rate_percentage', 'tax_amount',
            'total_amount', 'paid_amount', 'balance_due', 'balance_amount', 'status',
            'invoice_status', 'status_display', 'notes', 'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'tax_amount', 'total_amount', 'paid_amount', 'balance_due', 'created_at', 'updated_at']
