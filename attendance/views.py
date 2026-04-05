from django.shortcuts import render
from .models import Attendance
from accounts.decorators import admin_required
from django.utils.timezone import now

@admin_required
def today_attendance_list(request):
    today = now().date()
    # Fetch all records for today
    records = Attendance.objects.filter(date=today).select_related('employee__department', 'shift')
    return render(request, 'attendance/today_attendance_list.html', {
        'records': records,
        'today': today
    })

@admin_required
def attendance_history(request):
    # Fetch history (limited for performance)
    records = Attendance.objects.all().select_related('employee__department', 'shift')[:500]
    return render(request, 'attendance/attendance_history.html', {
        'records': records
    })
