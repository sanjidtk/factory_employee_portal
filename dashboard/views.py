from django.shortcuts import render
from django.utils.timezone import now
from django.http import JsonResponse

from employees.models import Employee
from attendance.models import Attendance
from overtime.models import Overtime


def dashboard_view(request):
    today = now().date()

    total_employees = Employee.objects.filter(is_active=True).count()

    today_attendance = Attendance.objects.filter(date=today)

    present_count = today_attendance.filter(status='P').count()
    absent_count = today_attendance.filter(status='A').count()
    leave_count = today_attendance.filter(status='L').count()

    on_time_count = today_attendance.filter(on_time_checkin=True).count()
    late_count = today_attendance.filter(
        status='P', on_time_checkin=False
    ).count()

    overtime_pending = Overtime.objects.filter(approval_status='P').count()
    overtime_approved = Overtime.objects.filter(approval_status='A').count()

    context = {
        "today": today,
        "total_employees": total_employees,
        "present_count": present_count,
        "absent_count": absent_count,
        "leave_count": leave_count,
        "on_time_count": on_time_count,
        "late_count": late_count,
        "overtime_pending": overtime_pending,
        "overtime_approved": overtime_approved,
    }

    return render(request, "dashboard/dashboard.html", context)


def dashboard_detail_view(request, tile):
    today = now().date()

    employees = []

    if tile == "all":
        qs = Employee.objects.filter(is_active=True)

    elif tile == "present":
        qs = Attendance.objects.filter(date=today, status='P')

    elif tile == "absent":
        qs = Attendance.objects.filter(date=today, status='A')

    elif tile == "leave":
        qs = Attendance.objects.filter(date=today, status='L')

    elif tile == "ontime":
        qs = Attendance.objects.filter(
            date=today, status='P', on_time_checkin=True
        )

    elif tile == "late":
        qs = Attendance.objects.filter(
            date=today, status='P', on_time_checkin=False
        )

    elif tile == "ot_pending":
        qs = Overtime.objects.filter(approval_status='P')

    elif tile == "ot_approved":
        qs = Overtime.objects.filter(approval_status='A')

    else:
        return JsonResponse({"employees": []})

    # Build response
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
                "department": record.employee.department.name
                if record.employee.department else "-"
            })

    return JsonResponse({"employees": employees})
