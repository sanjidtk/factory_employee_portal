from django.urls import path
from . import views

urlpatterns = [
    path('', views.shift_list, name='shift_list'),
]
