from django.contrib import admin
from .models import Invoice, Payment

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'group', 'policy', 'total_amount', 'paid_amount', 'balance_due', 'status', 'due_date')
    list_filter = ('status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'invoice', 'amount', 'payment_method', 'transaction_id', 'payment_date', 'status')
    list_filter = ('payment_method', 'status')
