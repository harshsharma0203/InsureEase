from django.db import models
from django.conf import settings
from decimal import Decimal
from policy_management.models import Policy
from members.models import Member


class ClaimType(models.TextChoices):
    REIMBURSEMENT = 'REIMBURSEMENT', 'Reimbursement Claim'
    CASHLESS = 'CASHLESS', 'Cashless Hospitalization'
    ACCIDENTAL_DEATH = 'ACCIDENTAL_DEATH', 'Accidental Death Benefit'
    DISABILITY = 'DISABILITY', 'Disability Benefit'
    CRITICAL_ILLNESS = 'CRITICAL_ILLNESS', 'Critical Illness Payout'


class ClaimStatus(models.TextChoices):
    SUBMITTED = 'Submitted', 'Submitted'
    UNDER_REVIEW = 'Under Review', 'Under Review'
    DOCUMENTS_REQUIRED = 'Documents Required', 'Documents Required'
    VERIFIED = 'Verified', 'Verified'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'
    SETTLEMENT_PENDING = 'Settlement Pending', 'Settlement Pending'
    SETTLED = 'Settled', 'Settled'


class Claim(models.Model):
    claim_number = models.CharField(max_length=50, unique=True, db_index=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='claims')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='claims')
    claim_type = models.CharField(max_length=30, choices=ClaimType.choices, db_index=True)
    incident_date = models.DateField()
    claim_submission_date = models.DateField(null=True, blank=True)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    diagnosis = models.CharField(max_length=255, blank=True, null=True)
    incident_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=30,
        default='Submitted',
        db_index=True
    )
    claim_status = models.CharField(
        max_length=30,
        choices=ClaimStatus.choices,
        default=ClaimStatus.SUBMITTED,
        db_index=True
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_claims'
    )
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_claims'
    )
    assigned_officer_id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='officer_claims'
    )
    verification_remarks = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    settlement_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'claims'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.incident_description and not self.description:
            self.description = self.incident_description
        elif self.description and not self.incident_description:
            self.incident_description = self.description
        if not self.claim_submission_date and self.created_at:
            self.claim_submission_date = self.created_at.date()
        if self.status and not self.claim_status:
            self.claim_status = self.status
        elif self.claim_status and not self.status:
            self.status = self.claim_status
        if self.assigned_officer and not self.assigned_officer_id_user:
            self.assigned_officer_id_user = self.assigned_officer
        elif self.assigned_officer_id_user and not self.assigned_officer:
            self.assigned_officer = self.assigned_officer_id_user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.claim_number} - {self.member.full_name} ({self.status})"


class ClaimDocument(models.Model):
    DOCUMENT_TYPES = [
        ('HOSPITAL_BILL', 'Hospital Discharge / Final Bill'),
        ('DIAGNOSTIC_REPORT', 'Investigation & Lab Reports'),
        ('PRESCRIPTION', 'Doctor Prescription'),
        ('FIR_COPY', 'Police FIR Copy'),
        ('KYC_DOC', 'KYC & Bank Passbook'),
        ('OTHER', 'Other Supporting Document'),
    ]

    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=150)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='claim_docs/', blank=True, null=True)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_claim_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claim_documents'
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if self.file_url and not self.file_path:
            self.file_path = self.file_url
        elif self.file_path and not self.file_url:
            self.file_url = self.file_path
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.claim.claim_number} - {self.document_name}"


class ClaimAssessment(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='assessments')
    assessor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    admissible_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    co_pay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    final_payable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    recommended_settlement = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    assessment_notes = models.TextField(blank=True, null=True)
    assessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claim_assessments'
        ordering = ['-assessed_at']

    def save(self, *args, **kwargs):
        if self.copay_amount is not None and (self.co_pay_amount is None or self.co_pay_amount == 0):
            self.co_pay_amount = self.copay_amount
        elif self.co_pay_amount is not None and (self.copay_amount is None or self.copay_amount == 0):
            self.copay_amount = self.co_pay_amount
        if self.final_payable is not None and (self.recommended_settlement is None or self.recommended_settlement == 0):
            self.recommended_settlement = self.final_payable
        elif self.recommended_settlement is not None and (self.final_payable is None or self.final_payable == 0):
            self.final_payable = self.recommended_settlement
        super().save(*args, **kwargs)


class ClaimSettlement(models.Model):
    claim = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name='settlement')
    settlement_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    settlement_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    bank_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_mode = models.CharField(max_length=30, default='NEFT_RTGS')
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number_masked = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_account = models.CharField(max_length=50, blank=True, null=True)
    beneficiary_ifsc = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default='PROCESSED')
    remarks = models.TextField(blank=True, null=True)
    settled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='settled_claims'
    )
    discharged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discharged_claims'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claim_settlements'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.bank_transaction_id and not self.payment_reference:
            self.payment_reference = self.bank_transaction_id
        elif self.payment_reference and not self.bank_transaction_id:
            self.bank_transaction_id = self.payment_reference
        if self.discharged_by and not self.settled_by:
            self.settled_by = self.discharged_by
        elif self.settled_by and not self.discharged_by:
            self.discharged_by = self.settled_by
        super().save(*args, **kwargs)
