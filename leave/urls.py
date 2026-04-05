from django.urls import path
from . import views

urlpatterns = [
    # HR Admin URLs
    path('admin/applications/', views.admin_applications_list, name='all_leave_applications'),
    path('admin/balances/', views.admin_balances_overview, name='all_leave_balances'),
    path('admin/allocate/', views.admin_allocate_leave, name='admin_allocate_leave'),
    
    # Employee URLs
    path('apply/', views.employee_apply, name='employee_apply'),
    path('my-leaves/', views.employee_history, name='employee_history'),
    path('my-balance/', views.employee_balance, name='employee_balance'),
]
