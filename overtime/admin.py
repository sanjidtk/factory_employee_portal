from django.contrib import admin
from .models import Overtime


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'date',
        'hours',
        'status',
        'created_at',
    )

    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__emp_id')

    # System-controlled fields (cannot be edited)
    readonly_fields = (
        'employee',
        'attendance',
        'created_at',
    )
    
    fieldsets = (
        ('Overtime Transaction', {
            'fields': ('employee', 'attendance', 'date', 'hours', 'reason', 'created_at')
        }),
        ('Administrative Action', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'decision_reason')
        }),
    )

    # Disable manual overtime creation
    def has_add_permission(self, request):
        return False


# ---------------------------
# ADMIN ACTIONS
# ---------------------------

@admin.action(description="Approve selected overtime")
def approve_overtime(modeladmin, request, queryset):
    queryset.update(status='Approved')


@admin.action(description="Reject selected overtime")
def reject_overtime(modeladmin, request, queryset):
    queryset.update(status='Rejected')


# Register actions
OvertimeAdmin.actions = [approve_overtime, reject_overtime]
