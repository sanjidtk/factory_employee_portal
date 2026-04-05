from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import admin_required, employee_required
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

from .models import LeaveApplication, LeaveBalance, LeaveType
from employees.models import Employee
from .forms import LeaveApplicationForm, LeaveAllocationForm, EmployeeLeaveApplicationForm

# ---------------------------------------------------------
# HR Admin Views
# ---------------------------------------------------------
@admin_required
def admin_applications_list(request):
    applications = LeaveApplication.objects.all().order_by('-applied_at')
    
    # Simple filters
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        action = request.POST.get('action') # 'Approve' or 'Reject'
        rejection_reason = request.POST.get('rejection_reason', '')
        
        application = get_object_or_404(LeaveApplication, id=app_id)
        if application.status == 'Pending':
            if action == 'Approve':
                application.status = 'Approved'
            elif action == 'Reject':
                application.status = 'Rejected'
                application.rejection_reason = rejection_reason
            
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            messages.success(request, f"Leave application {application.id} {action.lower()}d successfully.")
        return redirect('admin_applications_list')

    return render(request, 'leave/admin_applications.html', {'applications': applications})

@admin_required
def admin_balances_overview(request):
    balances = LeaveBalance.objects.all().order_by('employee__full_name', 'leave_type__name', '-year')
    return render(request, 'leave/admin_balances.html', {'balances': balances})

@admin_required
def admin_allocate_leave(request):
    if request.method == 'POST' and 'initialize_yearly' in request.POST:
        year = timezone.now().year
        leave_types = LeaveType.objects.all()
        employees = Employee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            for lt in leave_types:
                obj, created = LeaveBalance.objects.get_or_create(
                    employee=emp, leave_type=lt, year=year,
                    defaults={'allocated_days': lt.max_days_per_year}
                )
                if created:
                    count += 1
        messages.success(request, f"Successfully initialized {count} leave balance records for {year}.")
        return redirect('admin_balances_overview')

    if request.method == 'POST':
        form = LeaveAllocationForm(request.POST)
        if form.is_valid():
            balance = form.save()
            messages.success(request, f"Successfully allocated {balance.allocated_days} days to {balance.employee}.")
            return redirect('admin_balances_overview')
    else:
        form = LeaveAllocationForm(initial={'year': timezone.now().year})

    return render(request, 'leave/admin_allocate.html', {'form': form})

# ---------------------------------------------------------
# Employee Views
# ---------------------------------------------------------
@employee_required
def employee_apply(request):
    employee = request.user.employee
    if request.method == 'POST':
        form = EmployeeLeaveApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.employee = employee
            app.total_days = app.calculate_total_days()
            
            # Check overlap
            overlap = LeaveApplication.objects.filter(
                employee=app.employee,
                status__in=['Pending', 'Approved'],
                start_date__lte=app.end_date,
                end_date__gte=app.start_date
            ).exists()

            if overlap:
                messages.error(request, "You already have a leave application for these dates.")
                return render(request, 'leave/employee_apply.html', {'form': form, 'manager': employee.manager})

            # Check remaining balance warning (warn but do not block, HR can override)
            balance_record = LeaveBalance.objects.filter(
                employee=app.employee, 
                leave_type=app.leave_type, 
                year=app.start_date.year
            ).first()

            remaining = balance_record.remaining_days if balance_record else Decimal(0)
            if app.total_days > remaining:
                messages.warning(request, "Warning: You are applying for more days than your remaining balance. Subject to HR approval.")

            app.save()
            messages.success(request, "Leave application submitted successfully.")
            return redirect('employee_history')
    else:
        form = EmployeeLeaveApplicationForm()
    
    return render(request, 'leave/employee_apply.html', {'form': form, 'manager': employee.manager})

@employee_required
def employee_history(request):
    employee = request.user.employee
    applications = LeaveApplication.objects.filter(employee=employee).order_by('-applied_at')
    return render(request, 'leave/employee_history.html', {'employee': employee, 'applications': applications})

@employee_required
def employee_balance(request):
    employee = request.user.employee
    current_year = timezone.now().year
    balances = LeaveBalance.objects.filter(employee=employee, year=current_year)
    return render(request, 'leave/employee_balance.html', {'employee': employee, 'balances': balances, 'current_year': current_year})
