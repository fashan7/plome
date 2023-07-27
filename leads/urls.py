from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('lead_dashboard/', views.lead_dashboard, name='lead_dashboard'),
    path('lead/toggle/<int:lead_id>/', views.toggle_lead_status, name='toggle_lead_status'),
    path('deactivated_leads/', views.deactivated_leads, name='deactivated_leads'),
    path('facebook_leads/', views.facebook_leads, name='facebook_leads'),
    path('lead_edit/<int:lead_id>/', views.lead_edit, name='lead_edit'),
    path('import_leads/', views.import_leads, name='import_leads'),
    path('export_leads/<str:file_format>/', views.export_leads, name='export_leads'),
     path('complete_leads/',views.complete_leads, name='complete_leads'),
    
]



# from django.urls import path
# from .views import  lead_dashboard

# app_name = 'leads'

# urlpatterns = [
#     path('lead_dashboard/', lead_dashboard, name='lead_dashboard'),
#     # Rest of the URL patterns
# ]
