from django.contrib import admin
from .models import LeaveType, LeaveBalance, LeaveApplication

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_per_year', 'is_paid', 'carry_forward')
    search_fields = ('name',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('name', 'max_days_per_year', 'is_paid', 'carry_forward')
        }),
    )

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days')
    list_filter = ('year', 'leave_type')
    search_fields = ('employee__full_name', 'employee__employee_id')
    
    fieldsets = (
        ('Allocation Data', {
            'fields': ('employee', 'leave_type', 'year', 'allocated_days')
        }),
        ('Usage Tracking', {
            'fields': ('used_days', 'remaining_days')
        }),
    )

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'applied_at')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__full_name', 'employee__employee_id')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'reason')
        }),
        ('Administrative Action', {
            'fields': ('status', 'applied_at')
        }),
    )
    readonly_fields = ('applied_at',)
