from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path("attendance/", include("attendance.urls")),
    path("dashboard/", include("dashboard.admin_urls")),
    path("manager/dashboard/", include("dashboard.manager_urls")),
    path("employee/dashboard/", include("dashboard.employee_urls")),
    path("employees/", include("employees.urls")),
    path("shifts/", include("shifts.urls")),
    path("overtime/", include("overtime.urls")),
    path("leave/", include("leave.urls")),
]
