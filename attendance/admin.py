from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    exclude = ('on_time_checkin',)
    def worked_hours_display(self, obj):
        return obj.worked_hours()

    worked_hours_display.short_description = "Worked Hours"
    
    list_display = (
        'employee',
        'date',
        'status',
        'shift',
        'check_in_time',
        'check_out_time',
        'on_time_checkin',
        'worked_hours_display',
    )
    
    list_filter = ('date', 'status', 'shift', 'on_time_checkin')
    search_fields = ('employee__full_name', 'employee__employee_id')
    
    fieldsets = (
        ('Log Details', {
            'fields': ('employee', 'date', 'status', 'shift')
        }),
        ('Time Records', {
            'fields': ('check_in_time', 'check_out_time')
        }),
    )
