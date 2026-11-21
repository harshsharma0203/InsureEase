from django.contrib import admin
from .models import Endorsement

@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('endorsement_number', 'policy', 'endorsement_type', 'member', 'premium_adjustment', 'status', 'created_at')
    list_filter = ('endorsement_type', 'status')
