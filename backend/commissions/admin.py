from django.contrib import admin
from .models import Agent, Commission

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_code', 'name', 'agency_name', 'default_commission_rate', 'total_earned', 'total_paid', 'status')
    list_filter = ('status',)

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('commission_number', 'agent', 'policy', 'commission_amount', 'status', 'created_at')
    list_filter = ('status',)
