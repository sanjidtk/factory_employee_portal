from django.contrib import admin
from .models import Employee, Department

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'role', 'manager', 'is_active')
    search_fields = ('employee_id', 'full_name', 'role')
    list_filter = ('role', 'department', 'is_active')
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'full_name', 'employee_id')
        }),
        ('Job Details', {
            'fields': ('department', 'designation', 'role', 'manager')
        }),
        ('Status', {
            'fields': ('is_active', 'date_joined')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')
    search_fields = ('name',)
    list_filter = ('manager',)
    
    fieldsets = (
        ('General Information', {
            'fields': ('name', 'manager')
        }),
    )
