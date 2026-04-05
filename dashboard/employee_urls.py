from django.urls import path
from .views import (
    employee_dashboard_view, 
    employee_attendance_view, 
    employee_overtime_view, 
    employee_schedule_view
)

urlpatterns = [
    path('', employee_dashboard_view, name='employee_dashboard'),
    path('attendance/', employee_attendance_view, name='employee_attendance'),
    path('overtime/', employee_overtime_view, name='employee_overtime'),
    path('schedule/', employee_schedule_view, name='employee_schedule'),
]
