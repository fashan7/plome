from django.urls import path
from .views import  lead_add, lead_edit, lead_delete

app_name = 'leads'

urlpatterns = [
    # path('lead/', lead_list, name='lead_list'),
    path('lead_add/', lead_add, name='lead_add'),
    path('edit/<int:lead_id>/', lead_edit, name='lead_edit'),
    path('delete/<int:lead_id>/', lead_delete, name='lead_delete'),
]
