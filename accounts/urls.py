from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='root_login'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
