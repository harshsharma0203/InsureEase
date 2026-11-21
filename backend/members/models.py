from django.db import models
from django.conf import settings
from groups.models import InsuranceGroup


class MemberGender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'


class MemberStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    TERMINATED = 'TERMINATED', 'Terminated'


class Member(models.Model):
    member_code = models.CharField(max_length=50, unique=True, db_index=True)
    group = models.ForeignKey(InsuranceGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name_field = models.CharField(max_length=200, blank=True, null=True, db_column='full_name')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=MemberGender.choices)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    employee_id = models.CharField(max_length=50, db_index=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    date_of_joining = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_relationship = models.CharField(max_length=50, blank=True, null=True)
    nominee_phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=MemberStatus.choices,
        default=MemberStatus.ACTIVE,
        db_index=True
    )
    member_status = models.CharField(
        max_length=20,
        choices=MemberStatus.choices,
        default=MemberStatus.ACTIVE,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        ordering = ['-id']
        unique_together = ('group', 'employee_id')

    def save(self, *args, **kwargs):
        self.full_name_field = f"{self.first_name} {self.last_name}".strip()
        if self.phone and not self.phone_number:
            self.phone_number = self.phone
        elif self.phone_number and not self.phone:
            self.phone = self.phone_number
        if self.status and not self.member_status:
            self.member_status = self.status
        elif self.member_status and not self.status:
            self.status = self.member_status
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id}) - {self.group.name}"

    @property
    def full_name(self):
        return self.full_name_field or f"{self.first_name} {self.last_name}".strip()
