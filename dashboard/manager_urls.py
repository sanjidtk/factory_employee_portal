from django.urls import path
from .views import manager_dashboard_view, ajax_overtime_action, ajax_leave_action

urlpatterns = [
    path('', manager_dashboard_view, name='manager_dashboard'),
    path('ajax/overtime/<int:ot_id>/<str:action>/', ajax_overtime_action, name='ajax_overtime_action_manager'),
    path('ajax/leave/<int:leave_id>/<str:action>/', ajax_leave_action, name='ajax_leave_action_manager'),
]
