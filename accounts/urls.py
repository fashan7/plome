from django.urls import path, include
from .views import *


# app_name = 'accounts'

urlpatterns = [
    path('', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', signout, name='logout'),
    path('login/', login_request, name='login')
    

   
]

