from django.contrib import admin
from .models import Claim, ClaimDocument, ClaimAssessment, ClaimSettlement

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'policy', 'member', 'claim_type', 'claim_amount', 'approved_amount', 'status', 'incident_date')
    list_filter = ('claim_type', 'status')

@admin.register(ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    list_display = ('claim', 'document_name', 'document_type', 'uploaded_at')

@admin.register(ClaimAssessment)
class ClaimAssessmentAdmin(admin.ModelAdmin):
    list_display = ('claim', 'assessor', 'final_payable', 'assessed_at')

@admin.register(ClaimSettlement)
class ClaimSettlementAdmin(admin.ModelAdmin):
    list_display = ('claim', 'settlement_amount', 'settlement_date', 'payment_reference', 'payment_mode')
