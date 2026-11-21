from django.contrib import admin
from .models import (
    InsuranceProduct,
    PolicyApplication,
    UnderwritingRecord,
    Policy,
    PolicyMember,
    PolicyVersion
)

@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'coverage_type', 'base_rate_percentage', 'is_active')
    list_filter = ('coverage_type', 'is_active')

@admin.register(PolicyApplication)
class PolicyApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'group', 'product', 'total_members_count', 'status', 'created_at')
    list_filter = ('status', 'product')

@admin.register(UnderwritingRecord)
class UnderwritingRecordAdmin(admin.ModelAdmin):
    list_display = ('application', 'risk_score', 'risk_category', 'calculated_indicative_premium', 'decision')
    list_filter = ('decision', 'risk_category')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'group', 'product', 'total_sum_insured', 'total_premium', 'start_date', 'expiry_date', 'status')
    list_filter = ('status', 'product')

@admin.register(PolicyMember)
class PolicyMemberAdmin(admin.ModelAdmin):
    list_display = ('policy', 'member', 'coverage_amount', 'status')

@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ('policy', 'version_number', 'change_reason', 'effective_date')
