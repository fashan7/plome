from django.urls import path, include
from .views import *
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('advisor_dashboard/', advisor_dashboard, name='advisor_dashboard'),
    path('sales_dashboard/', sales_dashboard, name='sales_dashboard'),
    path('sadmin_dashboard/', sadmin_dashboard, name='sadmin_dashboard'),
    path('add_new_user/', add_new_user, name='add_new_user'),
    path('save_user/', save_user, name='save_user'),
    path('check_username/', check_username, name='check_username'),
    path('edit-user/<int:user_id>/', edit_user, name='edit-user'),
    path('delete-user/<int:user_id>/',delete_user, name='delete-user'),
    path('sendemail/', sendemail, name='sendemail'),
    path('profile/',profile,name ="profile"),
    path('profile_settings/',profile_settings,name ="profile_settings"),
    path('log_entry_list/', log_entry_list, name='log_entry_list'),
    path('get_notifications/', get_notifications, name='get_notifications'),
    path('mark_notification_read/', mark_notification_read, name='mark_notification_read'),
    path('clear_all_notifications/', clear_all_notifications, name='clear_all_notifications'),
    path('all_notifications/', all_notifications, name='all_notifications'),
    path('fetch_price_data', fetch_price_data, name='fetch_price_data'),
    path('activate-user/<int:user_id>/', activate_user, name='activate-user'),
    path('deactivate-user/<int:user_id>/', deactivate_user, name='deactivate-user'),
    path('toggle_user/<int:user_id>/', toggle_user, name='toggle_user'),
    path('activate-user/<int:user_id>/', activate_user, name='activate-user'),
    path('deactivate-user/<int:user_id>/', deactivate_user, name='deactivate-user'),
    path('deactivate_users/', deactivate_users, name='deactivate-users'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


