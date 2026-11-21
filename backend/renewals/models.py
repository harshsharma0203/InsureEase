from django.db import models
from django.conf import settings
from decimal import Decimal
from policy_management.models import Policy


class RenewalStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Application'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    COMPLETED = 'COMPLETED', 'Completed & Issued'
    EXPIRED = 'EXPIRED', 'Expired without Renewal'


class Renewal(models.Model):
    renewal_number = models.CharField(max_length=50, unique=True, db_index=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='renewals')
    previous_expiry_date = models.DateField(null=True, blank=True)
    proposed_start_date = models.DateField()
    proposed_expiry_date = models.DateField()
    previous_annual_premium = models.DecimalField(max_digits=12, decimal_places=2)
    previous_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    claims_ratio_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Historical claims / premium ratio percentage"
    )
    revised_premium = models.DecimalField(max_digits=12, decimal_places=2)
    revised_sum_insured = models.DecimalField(max_digits=14, decimal_places=2)
    reminder_count = models.PositiveIntegerField(default=0)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RenewalStatus.choices,
        default=RenewalStatus.PENDING,
        db_index=True
    )
    renewal_status = models.CharField(max_length=20, default='PENDING', db_index=True)
    renewed_policy = models.ForeignKey(
        Policy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='renewed_origin'
    )
    remarks = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_renewals'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_renewals'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'renewals'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.previous_annual_premium is not None and self.previous_premium is None:
            self.previous_premium = self.previous_annual_premium
        elif self.previous_premium is not None and self.previous_annual_premium is None:
            self.previous_annual_premium = self.previous_premium
        if self.status and not self.renewal_status:
            self.renewal_status = self.status
        elif self.renewal_status and not self.status:
            self.status = self.renewal_status
        if self.reviewed_by and not self.approved_by:
            self.approved_by = self.reviewed_by
        elif self.approved_by and not self.reviewed_by:
            self.reviewed_by = self.approved_by
        if not self.previous_expiry_date and self.policy:
            self.previous_expiry_date = self.policy.expiry_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.renewal_number} for {self.policy.policy_number} ({self.status})"
