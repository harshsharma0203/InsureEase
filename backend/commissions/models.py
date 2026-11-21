from django.db import models
from django.conf import settings
from decimal import Decimal
from policy_management.models import Policy
from billing.models import Invoice, Payment


class AgentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'


class CommissionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Approval'
    APPROVED = 'APPROVED', 'Approved'
    PAID = 'PAID', 'Paid'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Agent(models.Model):
    agent_code = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_profile'
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    agency_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, unique=True)
    default_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('8.50'),
        help_text="Standard commission rate %"
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=20,
        choices=AgentStatus.choices,
        default=AgentStatus.ACTIVE,
        db_index=True
    )
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agents'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.phone and not self.contact_number:
            self.contact_number = self.phone
        elif self.contact_number and not self.phone:
            self.phone = self.contact_number
        if self.default_commission_rate is not None and self.commission_rate is None:
            self.commission_rate = self.default_commission_rate
        elif self.commission_rate is not None and self.default_commission_rate is None:
            self.default_commission_rate = self.commission_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.agent_code}) - {self.agency_name}"


class Commission(models.Model):
    commission_number = models.CharField(max_length=50, unique=True, db_index=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='commissions')
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='commissions')
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions'
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commission_records'
    )
    eligible_premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
    eligible_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=CommissionStatus.choices,
        default=CommissionStatus.PENDING,
        db_index=True
    )
    commission_status = models.CharField(max_length=20, default='PENDING', db_index=True)
    approved_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_commissions'
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'commissions'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.eligible_premium_amount is not None and self.eligible_premium is None:
            self.eligible_premium = self.eligible_premium_amount
        elif self.eligible_premium is not None and self.eligible_premium_amount is None:
            self.eligible_premium_amount = self.eligible_premium
        if self.rate_percentage is not None and self.commission_rate is None:
            self.commission_rate = self.rate_percentage
        elif self.commission_rate is not None and self.rate_percentage is None:
            self.rate_percentage = self.commission_rate
        if self.status and not self.commission_status:
            self.commission_status = self.status
        elif self.commission_status and not self.status:
            self.status = self.commission_status
        if self.payment_date and not self.paid_date:
            self.paid_date = self.payment_date
        elif self.paid_date and not self.payment_date:
            self.payment_date = self.paid_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.commission_number} - {self.agent.name}: ₹{self.commission_amount} ({self.status})"
