from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('lead_dashboard/', views.lead_dashboard, name='lead_dashboard'),
    # path('gsheet/', views.gsheet, name="gsheet"),
    path('lead/toggle/<int:lead_id>/', views.toggle_lead_status, name='toggle_lead_status'),
    path('deactivated_leads/', views.deactivated_leads, name='deactivated_leads'),
    path('lead/sales_toggle/<int:lead_id>/', views.toggle_saleslead_status, name='toggle_saleslead_status'),    
    path('facebook_leads/', views.facebook_leads, name='facebook_leads'),
    path('lead_edit/<int:lead_id>/', views.lead_edit, name='lead_edit'),
    path('import_leads/', views.import_leads, name='import_leads'),
    path('export_leads/<str:file_format>/', views.export_leads, name='export_leads'),

    path('sales_lead/',views.sales_lead,name="sales_lead"),
    path('complete_leads/',views.complete_leads, name='complete_leads'),
    path('fetch_facebook_leads/', views.fetch_facebook_leads, name='fetch_facebook_leads'),
    path('filtered_lead_dashboard/<int:user_id>/', views.filtered_lead_dashboard, name='filtered_lead_dashboard'),
    path('lead_list/', views.lead_list, name='lead_list'),
    #path('lead_history/<int:lead_id>/', views.lead_history, name='lead_history'),
    path('get_all_users/', views.get_all_users, name='get_all_users'),
    path('transfer_leads/', views.transfer_leads, name='transfer_leads'),
    path('lead-history/<int:lead_id>/', views.lead_history_view, name='lead_history'),
    path('lead-otherhistory/<int:lead_id>/', views.lead_otherhistory_view, name='lead_otherhistory'),
    
    path('complete_leads/',views.complete_leads, name='complete_leads'),

    path('sales_lead/',views.sales_lead,name="sales_lead"),
    path('assign_leads/', views.assign_leads, name='assign_leads'),
    path('lead_dashboard/<int:lead_id>/', views.lead_dashboard, name='lead_dashboard'),
    
    path('attach_file/<int:lead_id>/', views.attach_file_to_lead, name='attach_file_to_lead'),
    path('download_attachment/<int:attachment_id>/<path:attachment_name>/', views.download_attachment, name='download_attachment'),
    path('delete_attachment/<int:attachment_id>/', views.delete_attachment, name='delete_attachment'),
    path('sales_dashboard/', views.sales_dashboard, name='sales_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('save_appointment/', views.save_appointment, name='save_appointment'),
    path('save_signe_cpf/', views.save_signe_cpf, name='save_signe_cpf'),
    path('view_notifications/', views.view_notifications, name='view_notifications'),
    path('get_qualification_data/', views.get_qualification_data, name='get_qualification_data'),
    path('send_appointment_reminder/', views.send_appointment_reminder, name='send_appointment_reminder'),
    
]





# from django.urls import path
# from .views import  lead_dashboard

# app_name = 'leads'

# urlpatterns = [
#     path('lead_dashboard/', lead_dashboard, name='lead_dashboard'),
#     # Rest of the URL patterns
# ]
