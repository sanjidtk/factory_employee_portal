from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.today_attendance_list, name='today_attendance'),
    path('history/', views.attendance_history, name='attendance_history'),
]
