from django.contrib import admin
from .models import Renewal

@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ('renewal_number', 'policy', 'previous_annual_premium', 'revised_premium', 'status')
    list_filter = ('status',)
