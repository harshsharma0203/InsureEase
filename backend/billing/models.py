from django.db import models
from django.conf import settings
from decimal import Decimal
from policy_management.models import Policy
from groups.models import InsuranceGroup


class InvoiceStatus(models.TextChoices):
    UNPAID = 'UNPAID', 'Unpaid'
    PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
    PAID = 'PAID', 'Paid'
    OVERDUE = 'OVERDUE', 'Overdue'
    CANCELLED = 'CANCELLED', 'Cancelled'


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = 'BANK_TRANSFER', 'Direct Bank Transfer'
    NEFT = 'NEFT', 'NEFT'
    RTGS = 'RTGS', 'RTGS'
    CHEQUE = 'CHEQUE', 'Corporate Cheque'
    CORPORATE_CARD = 'CORPORATE_CARD', 'Corporate Credit Card'
    UPI = 'UPI', 'Corporate UPI'


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='invoices')
    group = models.ForeignKey(InsuranceGroup, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'), help_text="GST %")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(max_digits=12, decimal_places=2)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.UNPAID,
        db_index=True
    )
    invoice_status = models.CharField(max_length=20, default='UNPAID', db_index=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']

    def save(self, *args, **kwargs):
        if self.subtotal_amount is not None and self.subtotal is None:
            self.subtotal = self.subtotal_amount
        elif self.subtotal is not None and self.subtotal_amount is None:
            self.subtotal_amount = self.subtotal
        if self.balance_due is not None and self.balance_amount is None:
            self.balance_amount = self.balance_due
        elif self.balance_amount is not None and self.balance_due is None:
            self.balance_due = self.balance_amount
        if self.status and not self.invoice_status:
            self.invoice_status = self.status
        elif self.invoice_status and not self.status:
            self.status = self.invoice_status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.group.name} (₹{self.total_amount})"


class Payment(models.Model):
    payment_reference = models.CharField(max_length=50, unique=True, db_index=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.NEFT)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    payer_name = models.CharField(max_length=150)
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('PENDING', 'Pending'), ('FAILED', 'Failed')],
        default='SUCCESS'
    )
    payment_status = models.CharField(max_length=20, default='SUCCESS')
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.amount is not None and self.payment_amount is None:
            self.payment_amount = self.amount
        elif self.payment_amount is not None and self.amount is None:
            self.amount = self.payment_amount
        if self.transaction_id and not self.transaction_reference:
            self.transaction_reference = self.transaction_id
        elif self.transaction_reference and not self.transaction_id:
            self.transaction_id = self.transaction_reference
        if self.status and not self.payment_status:
            self.payment_status = self.status
        elif self.payment_status and not self.status:
            self.status = self.payment_status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_reference} - ₹{self.amount} for {self.invoice.invoice_number}"
