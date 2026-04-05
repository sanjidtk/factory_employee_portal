from django.contrib import admin
from .models import Employee, Department, Designation

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name',)
    list_filter = ('department',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'first_name', 'last_name', 'department', 'designation', 'role', 'manager', 'is_active')
    search_fields = ('emp_id', 'first_name', 'last_name', 'role')
    list_filter = ('role', 'department', 'designation', 'is_active')
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'first_name', 'last_name', 'phone', 'email', 'emp_id')
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
