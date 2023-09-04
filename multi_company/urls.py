# multi_company/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('company_dropdown_view/', views.company_dropdown_view, name='company_dropdown_view'),
    # Add URL patterns for other company dashboards
]