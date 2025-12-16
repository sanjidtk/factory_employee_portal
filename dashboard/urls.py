from django.urls import path
from .views import dashboard_view, dashboard_detail_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path("detail/<str:tile>/", dashboard_detail_view,  name="dashboard_detail"),
]
