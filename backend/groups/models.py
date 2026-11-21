from django.db import models
from django.conf import settings


class GroupStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    SUSPENDED = 'SUSPENDED', 'Suspended'


class InsuranceGroup(models.Model):
    group_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    group_name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    registration_number = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=100, db_index=True)
    industry_type = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_groups'
    )
    group_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_insurance_groups'
    )
    employee_count = models.PositiveIntegerField(default=1)
    total_employees = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=GroupStatus.choices,
        default=GroupStatus.ACTIVE,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insurance_groups'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.name and not self.group_name:
            self.group_name = self.name
        elif self.group_name and not self.name:
            self.name = self.group_name
        if not self.organization_name:
            self.organization_name = self.name or self.group_name
        if self.industry and not self.industry_type:
            self.industry_type = self.industry
        elif self.industry_type and not self.industry:
            self.industry = self.industry_type
        if self.pincode and not self.postal_code:
            self.postal_code = self.pincode
        elif self.postal_code and not self.pincode:
            self.pincode = self.postal_code
        if self.employee_count and not self.total_employees:
            self.total_employees = self.employee_count
        elif self.total_employees and not self.employee_count:
            self.employee_count = self.total_employees
        if self.manager and not self.group_manager:
            self.group_manager = self.manager
        elif self.group_manager and not self.manager:
            self.manager = self.group_manager
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or self.group_name} ({self.group_code})"
