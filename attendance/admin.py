from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    readonly_fields = ('is_late', 'late_minutes')
    
    def worked_hours_display(self, obj):
        return obj.worked_hours()

    worked_hours_display.short_description = "Worked Hours"
    
    list_display = (
        'employee',
        'date',
        'status',
        'shift',
        'check_in',
        'check_out',
        'is_late',
        'late_minutes',
        'worked_hours_display',
    )
    
    list_filter = ('date', 'status', 'shift', 'is_late')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__emp_id')
    
    fieldsets = (
        ('Log Details', {
            'fields': ('employee', 'date', 'status', 'shift')
        }),
        ('Time Records', {
            'fields': ('check_in', 'check_out', 'is_late', 'late_minutes')
        }),
    )
