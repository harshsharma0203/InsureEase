from django.contrib import admin
from .models import InsuranceGroup

@admin.register(InsuranceGroup)
class InsuranceGroupAdmin(admin.ModelAdmin):
    list_display = ('group_code', 'name', 'industry', 'contact_person', 'employee_count', 'status')
    search_fields = ('name', 'group_code', 'registration_number')
    list_filter = ('industry', 'status')
