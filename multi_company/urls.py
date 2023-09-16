# multi_company/urls.py
from django.urls import path
from . import views 
from .views import GeneratePDF


urlpatterns = [
    path('company_dropdown_view/', views.company_dropdown_view, name='company_dropdown_view'),
    path('doisser/',views.doisser, name='doisser'),
    path('import_doisser_leads/', views.import_doisser_leads, name='import_doisser_leads'),
    path('contract_form/', views.contract_form_view, name='contract_form'),
     path('generate_pdf/', GeneratePDF.as_view(), name='generate_pdf'),
    # Add URL patterns for other company dashboards
]
