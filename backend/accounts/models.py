from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    INSURANCE_ADMIN = 'INSURANCE_ADMIN', 'Insurance Admin'
    UNDERWRITER = 'UNDERWRITER', 'Underwriter'
    CLAIMS_OFFICER = 'CLAIMS_OFFICER', 'Claims Officer'
    FINANCE_OFFICER = 'FINANCE_OFFICER', 'Finance Officer'
    GROUP_MANAGER = 'GROUP_MANAGER', 'Group Manager'
    POLICYHOLDER = 'POLICYHOLDER', 'Policyholder'


class User(AbstractUser):
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.POLICYHOLDER,
        db_index=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.phone and not self.phone_number:
            self.phone_number = self.phone
        elif self.phone_number and not self.phone:
            self.phone = self.phone_number
        if self.pincode and not self.postal_code:
            self.postal_code = self.pincode
        elif self.postal_code and not self.pincode:
            self.pincode = self.postal_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.details and not self.description:
            self.description = self.details
        elif self.description and not self.details:
            self.details = self.description
        super().save(*args, **kwargs)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"[{self.module}] {username}: {self.action} at {self.created_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, default='INFO')  # INFO, WARNING, SUCCESS, ALERT
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"
