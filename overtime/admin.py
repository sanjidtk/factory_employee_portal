from django.contrib import admin
from .models import Overtime


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'overtime_hours',
        'approval_status',
        'created_at',
    )

    list_filter = ('approval_status',)
    search_fields = ('employee__full_name',)

    # System-controlled fields (cannot be edited)
    readonly_fields = (
        'employee',
        'attendance',
        'overtime_hours',
        'created_at',
    )

    # Disable manual overtime creation
    def has_add_permission(self, request):
        return False

    # Allow editing only approval fields
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return super().get_readonly_fields(request, obj)


# ---------------------------
# ADMIN ACTIONS
# ---------------------------

@admin.action(description="Approve selected overtime")
def approve_overtime(modeladmin, request, queryset):
    queryset.update(approval_status='A')


@admin.action(description="Reject selected overtime")
def reject_overtime(modeladmin, request, queryset):
    queryset.update(approval_status='R')


# Register actions
OvertimeAdmin.actions = [approve_overtime, reject_overtime]
