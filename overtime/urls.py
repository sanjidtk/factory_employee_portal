from django.urls import path
from . import views

urlpatterns = [
    path('', views.overtime_list, name='overtime_list'),
]
