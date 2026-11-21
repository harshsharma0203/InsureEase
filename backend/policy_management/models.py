from django.db import models
from django.conf import settings
from decimal import Decimal
from groups.models import InsuranceGroup
from members.models import Member


class CoverageType(models.TextChoices):
    HEALTH = 'HEALTH', 'Group Health (Mediclaim)'
    ACCIDENT = 'ACCIDENT', 'Group Personal Accident'
    LIFE = 'LIFE', 'Group Term Life'
    CRITICAL_ILLNESS = 'CRITICAL_ILLNESS', 'Group Critical Illness'
    DISABILITY = 'DISABILITY', 'Group Disability Shield'


class ApplicationStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    ADDITIONAL_INFO_REQUIRED = 'ADDITIONAL_INFO_REQUIRED', 'Additional Information Required'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    ISSUED = 'ISSUED', 'Issued'


class PolicyStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    PENDING = 'Pending', 'Pending'
    EXPIRED = 'Expired', 'Expired'
    CANCELLED = 'Cancelled', 'Cancelled'
    SUSPENDED = 'Suspended', 'Suspended'


class RiskCategory(models.TextChoices):
    LOW = 'LOW', 'Low Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    HIGH = 'HIGH', 'High Risk'
    VERY_HIGH = 'VERY_HIGH', 'Very High Risk'


class InsuranceProduct(models.Model):
    product_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    coverage_type = models.CharField(max_length=30, choices=CoverageType.choices, db_index=True)
    insurance_type = models.CharField(max_length=50, blank=True, null=True)
    min_coverage = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100000.00'))
    minimum_coverage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_coverage = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('5000000.00'))
    maximum_coverage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    base_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.50'), help_text="Annual base premium rate %")
    base_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    policy_duration_months = models.PositiveIntegerField(default=12)
    eligibility_criteria = models.TextField()
    terms_and_conditions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.CharField(max_length=20, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insurance_products'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.name and not self.product_name:
            self.product_name = self.name
        elif self.product_name and not self.name:
            self.name = self.product_name
        if self.coverage_type and not self.insurance_type:
            self.insurance_type = self.coverage_type
        elif self.insurance_type and not self.coverage_type:
            self.coverage_type = self.insurance_type
        if self.min_coverage is not None and self.minimum_coverage is None:
            self.minimum_coverage = self.min_coverage
        elif self.minimum_coverage is not None and self.min_coverage is None:
            self.min_coverage = self.minimum_coverage
        if self.max_coverage is not None and self.maximum_coverage is None:
            self.maximum_coverage = self.max_coverage
        elif self.maximum_coverage is not None and self.max_coverage is None:
            self.max_coverage = self.maximum_coverage
        if self.base_premium is None and self.base_rate_percentage is not None:
            self.base_premium = self.base_rate_percentage
        self.status = 'ACTIVE' if self.is_active else 'INACTIVE'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.product_code})"


class PolicyApplication(models.Model):
    application_number = models.CharField(max_length=50, unique=True, db_index=True)
    group = models.ForeignKey(InsuranceGroup, on_delete=models.CASCADE, related_name='policy_applications')
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name='applications')
    requested_coverage_per_member = models.DecimalField(max_digits=12, decimal_places=2)
    requested_coverage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    proposed_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_members_count = models.PositiveIntegerField(default=1)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_applications'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applicant_policy_applications'
    )
    application_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    requested_duration = models.PositiveIntegerField(default=12)
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED,
        db_index=True
    )
    application_status = models.CharField(max_length=30, default='SUBMITTED', db_index=True)
    remarks = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    supporting_document = models.FileField(upload_to='application_docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_applications'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.requested_coverage_per_member and not self.requested_coverage:
            self.requested_coverage = self.requested_coverage_per_member
        elif self.requested_coverage and not self.requested_coverage_per_member:
            self.requested_coverage_per_member = self.requested_coverage
        if self.applied_by and not self.applicant:
            self.applicant = self.applied_by
        elif self.applicant and not self.applied_by:
            self.applied_by = self.applicant
        if self.status and not self.application_status:
            self.application_status = self.status
        elif self.application_status and not self.status:
            self.status = self.application_status
        if self.remarks and not self.description:
            self.description = self.remarks
        elif self.description and not self.remarks:
            self.remarks = self.description
        if not self.application_date and self.created_at:
            self.application_date = self.created_at.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_number} - {self.group.name}"


class UnderwritingRecord(models.Model):
    application = models.OneToOneField(PolicyApplication, on_delete=models.CASCADE, related_name='underwriting')
    underwriter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='underwritings'
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('35.00'))
    risk_category = models.CharField(max_length=20, choices=RiskCategory.choices, default=RiskCategory.LOW)
    industry_risk_factor = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    group_size_discount = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.05'))
    calculated_indicative_premium = models.DecimalField(max_digits=12, decimal_places=2)
    approved_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    assessed_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    decision = models.CharField(
        max_length=30,
        choices=[
            ('PENDING', 'Pending Review'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('INFO_REQUESTED', 'Information Requested')
        ],
        default='PENDING',
        db_index=True
    )
    decision_remarks = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    assessment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'underwriting_records'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.approved_premium is not None and self.assessed_premium is None:
            self.assessed_premium = self.approved_premium
        elif self.assessed_premium is not None and self.approved_premium is None:
            self.approved_premium = self.assessed_premium
        elif self.assessed_premium is None and self.calculated_indicative_premium is not None:
            self.assessed_premium = self.calculated_indicative_premium
        if self.decision_remarks and not self.remarks:
            self.remarks = self.decision_remarks
        elif self.remarks and not self.decision_remarks:
            self.decision_remarks = self.remarks
        if self.decision_date and not self.assessment_date:
            self.assessment_date = self.decision_date
        elif self.assessment_date and not self.decision_date:
            self.decision_date = self.assessment_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"UW-{self.application.application_number} ({self.decision})"


class Policy(models.Model):
    policy_number = models.CharField(max_length=50, unique=True, db_index=True)
    application = models.ForeignKey(
        PolicyApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_policies'
    )
    group = models.ForeignKey(InsuranceGroup, on_delete=models.CASCADE, related_name='policies')
    product = models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name='policies')
    sum_insured_per_member = models.DecimalField(max_digits=12, decimal_places=2)
    total_members_covered = models.PositiveIntegerField(default=1)
    total_sum_insured = models.DecimalField(max_digits=14, decimal_places=2)
    coverage_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    base_annual_premium = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="18% GST")
    total_premium = models.DecimalField(max_digits=12, decimal_places=2)
    annual_premium = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(db_index=True)
    expiry_date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        default='Active',
        db_index=True
    )
    policy_status = models.CharField(
        max_length=20,
        choices=PolicyStatus.choices,
        default=PolicyStatus.ACTIVE,
        db_index=True
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_policies_by_user'
    )
    terms_and_conditions = models.TextField(blank=True, null=True)
    policy_pdf = models.FileField(upload_to='policy_docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policies'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.total_sum_insured is not None and self.coverage_amount is None:
            self.coverage_amount = self.total_sum_insured
        elif self.coverage_amount is not None and self.total_sum_insured is None:
            self.total_sum_insured = self.coverage_amount
        if self.total_premium is not None and self.annual_premium is None:
            self.annual_premium = self.total_premium
        elif self.annual_premium is not None and self.total_premium is None:
            self.total_premium = self.annual_premium
        if self.status and not self.policy_status:
            self.policy_status = self.status
        elif self.policy_status and not self.status:
            self.status = self.policy_status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.policy_number} - {self.group.name}"


class PolicyMember(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='policy_members')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='policy_enrollments')
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    individual_premium = models.DecimalField(max_digits=10, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    effective_date = models.DateField()
    enrollment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('ENDORSED_OUT', 'Endorsed Out'),
            ('SUSPENDED', 'Suspended')
        ],
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'policy_members'
        unique_together = ('policy', 'member')
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.individual_premium is not None and self.premium_amount is None:
            self.premium_amount = self.individual_premium
        elif self.premium_amount is not None and self.individual_premium is None:
            self.individual_premium = self.premium_amount
        if self.effective_date and not self.enrollment_date:
            self.enrollment_date = self.effective_date
        elif self.enrollment_date and not self.effective_date:
            self.effective_date = self.enrollment_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.full_name} in {self.policy.policy_number}"


class PolicyVersion(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    snapshot_data = models.JSONField(help_text="Complete JSON snapshot of policy state")
    change_reason = models.CharField(max_length=255)
    effective_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'policy_versions'
        unique_together = ('policy', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.policy.policy_number} v{self.version_number}"
