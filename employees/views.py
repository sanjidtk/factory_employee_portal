from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .models import Employee, Department
from .forms import AdminAddEmployeeForm, AdminEditEmployeeForm
from accounts.decorators import admin_required

@admin_required
def employee_list(request):
    employees = Employee.objects.all().select_related('department', 'manager')
    return render(request, 'employees/employee_list.html', {'employees': employees})

@admin_required
def department_list(request):
    departments = Department.objects.all().select_related('manager')
    return render(request, 'employees/department_list.html', {'departments': departments})

@admin_required
def designation_list(request):
    # Aggregate unique designations from the Employee model
    designations = Employee.objects.values_list('designation', flat=True).distinct()
    return render(request, 'employees/designation_list.html', {'designations': designations})

@admin_required
def admin_add_employee(request):
    if request.method == 'POST':
        form = AdminAddEmployeeForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        email=form.cleaned_data['email'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                    
                    # Create Employee Profile
                    Employee.objects.create(
                        user=user,
                        employee_id=form.cleaned_data['employee_id'],
                        department=form.cleaned_data['department'],
                        designation=form.cleaned_data['designation'],
                        role=form.cleaned_data['role'],
                        manager=form.cleaned_data['manager'],
                        date_joined=form.cleaned_data['date_joined'],
                        full_name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}".strip()
                    )
                messages.success(request, f"Employee {user.username} created successfully.")
                return redirect('employee_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminAddEmployeeForm()
        
    return render(request, 'employees/admin_add_employee.html', {'form': form})

@admin_required
def admin_view_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    return render(request, 'employees/admin_view_employee.html', {'employee': employee})

@admin_required
def admin_edit_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    user = employee.user
    
    if request.method == 'POST':
        form = AdminEditEmployeeForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    if user:
                        user.first_name = form.cleaned_data['first_name']
                        user.last_name = form.cleaned_data.get('last_name', '')
                        user.email = form.cleaned_data.get('email', '')
                        user.save()
                        
                    employee.department = form.cleaned_data['department']
                    employee.designation = form.cleaned_data['designation']
                    employee.role = form.cleaned_data['role']
                    employee.manager = form.cleaned_data['manager']
                    employee.date_joined = form.cleaned_data['date_joined']
                    employee.is_active = form.cleaned_data['is_active']
                    employee.full_name = f"{form.cleaned_data['first_name']} {form.cleaned_data.get('last_name', '')}".strip()
                    employee.save()
                    
                messages.success(request, f"Employee {employee.full_name} updated successfully.")
                return redirect('admin_view_employee', emp_id=employee.id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {
            'first_name': user.first_name if user else '',
            'last_name': user.last_name if user else '',
            'email': user.email if user else '',
            'employee_id': employee.employee_id,
            'department': employee.department,
            'designation': employee.designation,
            'role': employee.role,
            'manager': employee.manager,
            'date_joined': employee.date_joined,
            'is_active': employee.is_active,
        }
        form = AdminEditEmployeeForm(initial=initial_data)
        
    return render(request, 'employees/admin_edit_employee.html', {'form': form, 'employee': employee})
