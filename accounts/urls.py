from django.urls import path, include
from .views import *


# app_name = 'accounts'

urlpatterns = [
    path('', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', signout, name='logout'),
    path('login/', login_request, name='login'),
    path('reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

   
]

