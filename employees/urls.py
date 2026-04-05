from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('add/', views.admin_add_employee, name='admin_add_employee'),
    path('<int:emp_id>/', views.admin_view_employee, name='admin_view_employee'),
    path('<int:emp_id>/edit/', views.admin_edit_employee, name='admin_edit_employee'),
    path('departments/', views.department_list, name='department_list'),
    path('designations/', views.designation_list, name='designation_list'),
]
