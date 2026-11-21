from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_code', 'first_name', 'last_name', 'employee_id', 'group', 'status')
    search_fields = ('first_name', 'last_name', 'employee_id', 'member_code', 'group__name')
    list_filter = ('status', 'group')
