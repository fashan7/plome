from django.urls import path, include
from .views import *

urlpatterns = [
    path('set-priviledge/', setup_privilege, name='setup_privilege'),
    path('get-page-priv/', get_page_priv, name="get_page_priv")
]
