# multi_company/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('company_dropdown_view/', views.company_dropdown_view, name='company_dropdown_view'),
    path('doisser/',views.doisser, name='doisser'),
    path('import_doisser_leads/', views.import_doisser_leads, name='import_doisser_leads'),
    # Add URL patterns for other company dashboards
]
