from rest_framework import permissions
from .models import UserRole


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role == UserRole.SUPER_ADMIN or request.user.is_superuser
        ))


class IsInsuranceAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSURANCE_ADMIN] or request.user.is_superuser
        ))


class IsUnderwriter(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSURANCE_ADMIN, UserRole.UNDERWRITER]
        ))


class IsClaimsOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSURANCE_ADMIN, UserRole.CLAIMS_OFFICER]
        ))


class IsFinanceOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSURANCE_ADMIN, UserRole.FINANCE_OFFICER]
        ))


class IsGroupManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.INSURANCE_ADMIN, UserRole.GROUP_MANAGER]
        ))


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.role in [
                UserRole.SUPER_ADMIN,
                UserRole.INSURANCE_ADMIN,
                UserRole.UNDERWRITER,
                UserRole.CLAIMS_OFFICER,
                UserRole.FINANCE_OFFICER
            ] or request.user.is_staff or request.user.is_superuser
        ))


def log_activity(user, action, module, details="", ip_address=None):
    from .models import ActivityLog
    try:
        ActivityLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            module=module,
            details=details,
            ip_address=ip_address
        )
    except Exception as e:
        print(f"Error logging activity: {e}")
