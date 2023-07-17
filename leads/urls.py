from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('lead_dashboard/', views.lead_dashboard, name='lead_dashboard'),
   path('lead/delete/<int:lead_id>/', views.delete_lead, name='lead_delete'),


]

# from django.urls import path
# from .views import  lead_dashboard

# app_name = 'leads'

# urlpatterns = [
#     path('lead_dashboard/', lead_dashboard, name='lead_dashboard'),
#     # Rest of the URL patterns
# ]
