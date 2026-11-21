from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ActivityLog, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('InsureEase Profile', {'fields': ('role', 'phone', 'company_name', 'employee_id', 'address', 'city', 'state', 'pincode')}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'module', 'created_at')
    list_filter = ('module', 'created_at')
    search_fields = ('action', 'details', 'user__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type')
