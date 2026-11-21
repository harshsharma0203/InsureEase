from django.db import models
from django.conf import settings
from decimal import Decimal
from policy_management.models import Policy
from members.models import Member


class EndorsementType(models.TextChoices):
    ADD_MEMBER = 'ADD_MEMBER', 'Add Insured Member'
    REMOVE_MEMBER = 'REMOVE_MEMBER', 'Remove Insured Member'
    MODIFY_MEMBER = 'MODIFY_MEMBER', 'Modify Member Details'
    CHANGE_COVERAGE = 'CHANGE_COVERAGE', 'Change Coverage Amount'
    UPDATE_NOMINEE = 'UPDATE_NOMINEE', 'Update Nominee Info'
    UPDATE_GROUP = 'UPDATE_GROUP', 'Update Group Details'


class EndorsementStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Review'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    COMPLETED = 'COMPLETED', 'Completed'


class Endorsement(models.Model):
    endorsement_number = models.CharField(max_length=50, unique=True, db_index=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='endorsements')
    endorsement_type = models.CharField(max_length=30, choices=EndorsementType.choices, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='endorsements')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_endorsements'
    )
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    reason = models.TextField()
    effective_date = models.DateField()
    changes_data = models.JSONField(
        default=dict,
        help_text="Structured JSON capturing previous and new values"
    )
    premium_adjustment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Positive for additional premium, negative for refund"
    )
    status = models.CharField(
        max_length=20,
        choices=EndorsementStatus.choices,
        default=EndorsementStatus.PENDING,
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_endorsements'
    )
    review_notes = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'endorsements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.endorsement_number} - {self.get_endorsement_type_display()} ({self.policy.policy_number})"
