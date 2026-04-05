from django.urls import path
from .views import (
    dashboard_view, dashboard_detail_view, ajax_overtime_action, 
    ajax_leave_action, admin_roster, admin_assignments
)

urlpatterns = [
    path('', dashboard_view, name='admin_dashboard'),
    path('detail/<str:tile>/', dashboard_detail_view, name='admin_dashboard_detail'),
    path('roster/', admin_roster, name='admin_roster'),
    path('assignments/', admin_assignments, name='admin_assignments'),
    path('ajax/overtime/<int:ot_id>/<str:action>/', ajax_overtime_action, name='ajax_overtime_action_admin'),
    path('ajax/leave/<int:leave_id>/<str:action>/', ajax_leave_action, name='ajax_leave_action_admin'),
]
