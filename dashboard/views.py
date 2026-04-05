from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Prefetch
from django.views.decorators.http import require_POST
import json

from accounts.decorators import admin_required, manager_required, employee_required
from employees.models import Employee
from attendance.models import Attendance
from overtime.models import Overtime
from leave.models import LeaveApplication, LeaveBalance

@admin_required
def dashboard_view(request):
    today = now().date()
    
    total_employees = Employee.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=today).select_related('employee__department')
    
    present_count = today_attendance.filter(status='Present').count()
    absent_count = today_attendance.filter(status='Absent').count()
    leave_count = today_attendance.filter(status='On Leave').count()
    
    on_time_count = today_attendance.filter(is_late=False, status='Present').count()
    late_count = today_attendance.filter(status='Late').count()
    
    pending_overtimes = Overtime.objects.filter(status='Pending').select_related('employee')
    overtime_pending_count = pending_overtimes.count()
    overtime_approved = Overtime.objects.filter(status='Approved').count()
    
    pending_leaves = LeaveApplication.objects.filter(status='Pending').select_related('employee', 'leave_type')
    leave_pending_count = pending_leaves.count()
    
    context = {
        "today": today,
        "total_employees": total_employees,
        "present_count": present_count,
        "absent_count": absent_count,
        "leave_count": leave_count,
        "on_time_count": on_time_count,
        "late_count": late_count,
        "overtime_pending": overtime_pending_count,
        "overtime_approved": overtime_approved,
        "today_attendance": today_attendance,
        "pending_overtimes": pending_overtimes,
        "pending_leaves": pending_leaves,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@manager_required
def manager_dashboard_view(request):
    today = now().date()
    employee = request.user.employee

    # Direct reports (employees who have this manager explicitly assigned via FK)
    direct_reports = Employee.objects.filter(manager=employee, is_active=True).select_related('department')
    direct_report_ids = list(direct_reports.values_list('id', flat=True))

    # Team overview: preferably direct reports; fallback to same department employees
    if direct_report_ids:
        team_members = direct_reports
        team_ids = direct_report_ids
        using_dept_fallback = False
    elif employee.department:
        team_members = Employee.objects.filter(
            department=employee.department, is_active=True, role='employee'
        ).exclude(id=employee.id).select_related('department')
        team_ids = list(team_members.values_list('id', flat=True))
        using_dept_fallback = True
    else:
        team_members = Employee.objects.filter(is_active=True, role='employee').exclude(id=employee.id).select_related('department')
        team_ids = list(team_members.values_list('id', flat=True))
        using_dept_fallback = True

    # Team today attendance
    team_attendance = Attendance.objects.filter(date=today, employee_id__in=team_ids)
    attendance_map = {att.employee_id: att for att in team_attendance}
    for member in team_members:
        member.today_attendance = attendance_map.get(member.id)

    # ALL pending leaves visible to this manager (from team scope above)
    pending_leaves = LeaveApplication.objects.filter(
        employee_id__in=team_ids,
        status='Pending'
    ).select_related('employee', 'leave_type').order_by('-applied_at')

    # ALL pending overtime from same scope
    pending_overtimes = Overtime.objects.filter(
        employee_id__in=team_ids,
        status='Pending'
    ).select_related('employee')

    context = {
        "team_members": team_members,
        "pending_leaves": pending_leaves,
        "pending_overtimes": pending_overtimes,
        "today": today,
        "manager": employee,
        "has_team": len(team_ids) > 0,
        "using_dept_fallback": using_dept_fallback,
        "pending_leave_count": pending_leaves.count(),
        "pending_ot_count": pending_overtimes.count(),
    }
    return render(request, "dashboard/manager_dashboard.html", context)


@employee_required
def employee_dashboard_view(request):
    today = now().date()
    employee = request.user.employee
    
    # Today's status
    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    # Leave balances
    balances = LeaveBalance.objects.filter(employee=employee, year=today.year).select_related('leave_type')
    
    # Recent requests
    recent_leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_at')[:5]
    recent_overtimes = Overtime.objects.filter(employee=employee).order_by('-created_at')[:5]
    
    context = {
        "employee": employee,
        "today": today,
        "today_attendance": today_attendance,
        "leave_balances": balances,
        "recent_leaves": recent_leaves,
        "recent_overtimes": recent_overtimes,
    }
    return render(request, "dashboard/employee_dashboard.html", context)
    

@employee_required
def employee_attendance_view(request):
    employee = request.user.employee
    # Last 30 days attendance
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    return render(request, "dashboard/employee_attendance.html", {
        "employee": employee,
        "records": attendance_records
    })

@employee_required
def employee_overtime_view(request):
    employee = request.user.employee
    # Last 30 days overtime requests
    ot_records = Overtime.objects.filter(employee=employee).order_by('-created_at')[:30]
    return render(request, "dashboard/employee_overtime.html", {
        "employee": employee,
        "records": ot_records
    })

@employee_required
def employee_schedule_view(request):
    employee = request.user.employee
    # Get current shift
    # For now we'll assume a basic logic, later we can integrate with a proper Roster model
    return render(request, "dashboard/employee_schedule.html", {
        "employee": employee
    })


@admin_required
def dashboard_detail_view(request, tile):
    today = now().date()
    employees = []

    if tile == "all":
        qs = Employee.objects.filter(is_active=True)
    elif tile == "present":
        qs = Attendance.objects.filter(date=today, status='Present')
    elif tile == "absent":
        qs = Attendance.objects.filter(date=today, status='Absent')
    elif tile == "leave":
        qs = Attendance.objects.filter(date=today, status='On Leave')
    elif tile == "ontime":
        qs = Attendance.objects.filter(date=today, status='Present', is_late=False)
    elif tile == "late":
        qs = Attendance.objects.filter(date=today, status='Late')
    elif tile == "ot_pending":
        qs = Overtime.objects.filter(status='Pending')
    elif tile == "ot_approved":
        qs = Overtime.objects.filter(status='Approved')
    else:
        return JsonResponse({"employees": []})

    if tile == "all":
        for emp in qs:
            employees.append({
                "name": emp.full_name,
                "department": emp.department.name if emp.department else "-"
            })
    else:
        for record in qs:
            employees.append({
                "name": record.employee.full_name,
                "department": record.employee.department.name if record.employee.department else "-"
            })

    return JsonResponse({"employees": employees})


@require_POST
def ajax_overtime_action(request, ot_id, action):
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'employee') and user.employee.role == 'admin')
    is_manager = hasattr(user, 'employee') and user.employee.role == 'manager'

    if not (is_admin or is_manager):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    ot = get_object_or_404(Overtime, id=ot_id)

    # Managers: verify authority via direct report OR same dept OR broadest fallback
    if is_manager and not is_admin:
        mgr_emp = user.employee
        applicant = ot.employee
        direct_report = applicant.manager == mgr_emp
        same_dept = (applicant.department == mgr_emp.department and applicant.role == 'employee')
        has_any_direct_reports = Employee.objects.filter(manager=mgr_emp, is_active=True).exists()
        if not (direct_report or same_dept or not has_any_direct_reports):
            return JsonResponse({'status': 'error', 'message': 'Not your team member'}, status=403)

    if action == 'approve':
        ot.status = 'Approved'
    elif action == 'reject':
        ot.status = 'Rejected'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    ot.save()
    return JsonResponse({'status': 'success', 'message': f'Overtime {action}d successfully'})


@admin_required
def admin_roster(request):
    today = now().date()
    # For now, roster is represented by today's attendance records with shift info
    roster_data = Attendance.objects.filter(date=today).select_related('employee__department', 'shift')
    return render(request, 'dashboard/admin_roster.html', {
        'today': today,
        'roster': roster_data
    })


@admin_required
def admin_assignments(request):
    today = now().date()
    # Assignments could be department assignments
    employees = Employee.objects.filter(is_active=True).select_related('department')
    return render(request, 'dashboard/admin_assignments.html', {
        'today': today,
        'employees': employees
    })


@require_POST
def ajax_leave_action(request, leave_id, action):
    user = request.user
    is_admin = user.is_superuser or (hasattr(user, 'employee') and user.employee.role == 'admin')
    is_manager = hasattr(user, 'employee') and user.employee.role == 'manager'

    if not (is_admin or is_manager):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    leave = get_object_or_404(LeaveApplication, id=leave_id)

    # Managers: verify they have authority over this employee
    if is_manager and not is_admin:
        mgr_emp = user.employee
        applicant = leave.employee
        direct_report = applicant.manager == mgr_emp
        same_dept = (applicant.department == mgr_emp.department and applicant.role == 'employee')
        # Broadest fallback: if NO direct reports at all exist for this manager,
        # allow them to approve any employee-role leave request
        has_any_direct_reports = Employee.objects.filter(manager=mgr_emp, is_active=True).exists()
        if not (direct_report or same_dept or not has_any_direct_reports):
            return JsonResponse({'status': 'error', 'message': 'Not your team member'}, status=403)

    data = {}
    if request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            pass

    if action == 'approve':
        leave.status = 'Approved'
        leave.reviewed_by = user
        leave.reviewed_at = now()
    elif action == 'reject':
        leave.status = 'Rejected'
        leave.reviewed_by = user
        leave.reviewed_at = now()
        leave.rejection_reason = data.get('rejection_reason', '')
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    leave.save()
    return JsonResponse({'status': 'success', 'message': f'Leave application {action}d successfully'})

