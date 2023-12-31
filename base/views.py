
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import CustomUserTypes
from pagesallocation.models import PageAllocation,Privilege
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse

from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.hashers import make_password

from leads.models import Lead,PriceEntry
from django.contrib import messages
from leads.models import Notification

from django.contrib.admin.models import LogEntry

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db.models import Count
from django.db.models.functions import Trunc
from django.views.decorators.http import require_POST

from django.utils.timezone import now
from django.utils.timezone import make_aware
from datetime import timedelta, datetime
from django.utils import timezone
#from leads.views import sales_lead
from django.db.models import F
from django.db.models import Sum


@require_POST
def clear_all_notifications(request):
    user = request.user
    Notification.objects.filter(user=user, is_hidden=False).update(is_hidden=True)

    return JsonResponse({'success': True})

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def all_notifications(request):
    # Read all notifications when view all
    user = request.user
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    
    # Check if the user is an admin (superuser)
    if user.is_superuser:
        # Redirect admin to lead_dashboard
        return redirect('lead_dashboard')
    else:
        # Redirect sales user to sales_lead
        return redirect('sales_lead')

@login_required
def get_notifications(request):
    user = request.user
    current_time = timezone.now()

    # Define the time range for each notification group (1 hour in this case)
    time_range = timedelta(hours=1)

    # Calculate the start and end times for the current hour
    current_time_naive = current_time.replace(minute=0, second=0, microsecond=0)  # Create naive datetime
    start_time = current_time_naive
    end_time = start_time + time_range

    # Fetch the notifications for the current hour
    unread_notifications = (
        Notification.objects.filter(user=user, is_hidden=False) #, timestamp__range=(start_time, end_time)
        .annotate(hour=Trunc('timestamp', 'hour'))
        .values('hour')
        .annotate(count=Count('id'))
        .annotate(lead_id=F('lead__id'))
        .values('hour', 'count', 'message', 'timestamp', 'id', 'is_read', 'lead_id')
        .order_by('-timestamp')
    )
    return JsonResponse(list(unread_notifications), safe=False)

@require_POST
def mark_notification_read(request):
    notification_id = request.POST.get('notification_id')

    try:
        notification = Notification.objects.get(pk=notification_id)
        notification.is_read = True
        notification.save()

        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
def admin_dashboard(request):
    if request.user.is_authenticated:
        filtered_user = CustomUserTypes.objects.filter(username=request.user)
        user = request.user
        context = {
        'user': user
        # ... other context variables ...
        }
        return render(request, 'base/admin_dashboard.html', context, locals())
    else:
        return render(request, '/login')
    
@login_required
def add_new_user(request):
    if request.user.is_authenticated:
        filtered_user = CustomUserTypes.objects.filter(username=request.user)
        view_all_users = CustomUserTypes.objects.exclude(username=request.user)
        return render(request, 'base/add_new_user.html', locals())
    else:
        return render(request, 'base/add_new_user.html')


@login_required
def log_entry_list(request):
    log_entries = LogEntry.objects.all()
    #print("___________________",log_entries)
    return render(request,'base/log_entry_list.html',{'log_entries':log_entries})


def set_privilege(user_id):
    pages = PageAllocation.objects.all()
    for page in pages:
        privilege = Privilege()
        privilege.pageallocation = page
        privilege.assigned_users = User.objects.get(id=user_id)
        privilege.save()

@csrf_exempt
def check_username(request):
    username = request.POST.get('Username')
    if CustomUserTypes.objects.filter(username=username).exists():
        return HttpResponse("false")
    else:
        return HttpResponse("true")
        

def save_user(request):
    if request.method == 'POST':
        # Retrieve form data from the request
        username = request.POST['Username']
        email = request.POST['Email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        user_type = request.POST['user_type']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # print(username, email, firstname, lastname, user_type, password, confirm_password)


        if password != confirm_password:
            # messages.error(request, "Passwords do not match.")
            print("Passwords do not match.")
            return redirect('add_new_user')

        try:
            if CustomUserTypes.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                print("Username already exists.")
                return redirect('add_new_user')

            if CustomUserTypes.objects.filter(email=email).exists():
                # messages.error(request, "Email already exists.")
                print("Email already exists.")
                return redirect('add_new_user')

            new_user = CustomUserTypes()
            new_user.username = username
            new_user.email = email
            new_user.first_name = firstname
            new_user.last_name = lastname

            if user_type == 'Advisor':
                new_user.is_advisor = True
            elif user_type == 'Sales':
                new_user.is_sales = True
            elif user_type == 'Admin':
                new_user.is_admin = True
            new_user.set_password(password)        
            new_user.save()

            set_privilege(new_user.id)

        except Exception as e:
            messages.error(request, "An error occurred while saving the user.")
            # Log the error or perform any other necessary actions
            return redirect('add_new_user')
    return redirect('add_new_user')

@login_required
def advisor_dashboard(request):
    return render(request, 'base/advisor_dashboard.html')

@login_required
def sales_dashboard(request):
    user_leads = Lead.objects.filter(assigned_to=request.user)

    # Calculate the number of new leads
    # new_leads_count = user_leads.filter(is_new=True).count()

    # Fetch the notification message for the current user from the session
    assigned_message = request.session.get('assigned_message', None)

    # Remove the notification message from the session
    if assigned_message:
        del request.session['assigned_message']

    context = {
        'user_leads': user_leads,
        'assigned_message': assigned_message,
        # 'new_leads_count': new_leads_count,
    }

    return render(request, 'base/sales_dashboard.html', context)

@login_required
def sadmin_dashboard(request):
    return render(request, 'base/sadmin_dashboard.html')



User = get_user_model()

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Update the user fields
        user.username = request.POST['Username']
        user.email = request.POST['Email']
        user.first_name = request.POST['firstname']
        user.last_name = request.POST['lastname']

        # Check if user type is included in the request
        user_type = request.POST.get('user_type', '')

        if user_type == 'Sales':
            user.is_sales = True
            user.is_advisor = False
            user.is_admin = False
        elif user_type == 'Advisor':
            user.is_sales = False
            user.is_advisor = True
            user.is_admin = False
        elif user_type == 'Admin':
            user.is_sales = False
            user.is_advisor = False
            user.is_admin = True
            
        password = request.POST.get('password')
        if password:
            user.password = make_password(password)

        user.save()

        return JsonResponse({'success': True})

    return render(request, 'base/edit_user.html', {'user': user})




# def edit_user(request, user_id):
#     user = get_object_or_404(User, id=user_id)

#     if request.method == 'POST':
#         # Update the user fields
#         user.username = request.POST['Username']
#         user.email = request.POST['Email']
#         user.first_name = request.POST['firstname']
#         user.last_name = request.POST['lastname']
#         user.is_sales = request.POST.get('user_type') == 'Sales'
#         user.is_advisor = request.POST.get('user_type') == 'Advisor'
#         user.is_admin = request.POST.get('user_type') == 'Admin'
#         user.save()

#         return JsonResponse({'success': True})

#     return render(request, 'base/edit_user.html', {'user': user})




def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Delete the user
        user.delete()

        return JsonResponse({'message': 'User deleted successfully.'})

    return JsonResponse({'error': 'Invalid request.'})


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def sendemail(request):
    user_id = request.GET.get('user_id')  # Get the user_id from the query parameters
    user = User.objects.get(id=user_id)  # Retrieve the user based on the user_id

    # Generate a one-time use link for password reset
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = request.get_host()  # Get the domain from the request
    password_reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
    password_reset_confirm_url = f'http://{domain}{password_reset_confirm_url}'  # Construct the complete URL
    # password_reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

    subject = 'Password Reset'
    html_message = render_to_string('base/email_template.html', {'user': user, 'password_reset_confirm_url': password_reset_confirm_url})
    plain_message = strip_tags(html_message)
    from_email = 'your-email@gmail.com'
    to_email = user.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return render(request, 'base/sendemail.html')


@login_required
def profile(request):
    # Check if the user is authenticated (logged in)
    if request.user.is_authenticated:
        # Get the user's profile (no need to use .profile since request.user is an instance of CustomUserTypes)
        user = request.user

        return render(request, 'base/profile.html', {'user': user})

    # If the user is not logged in, you can redirect them to the login page or handle it as you prefer
    # For example, you can redirect them to the homepage with a message
    # return redirect('home')
    return render(request, 'base/profile.html')  # You can pass an empty dictionary if you don't need to display any profile info



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def profile_settings(request):
    user = request.user
    is_sales = user.groups.filter(name='Sales').exists()  # Assuming Sales group exists for sales users
    is_super_admin = user.is_superuser

    if request.method == 'POST':
        # Update the user fields
        user.first_name = request.POST.get('firstname', '')
        user.last_name = request.POST.get('lastname', '')
        user.email = request.POST.get('inputEmail4', '')
        # Update other fields as needed

        # Check if the password fields are provided and match
        new_password = request.POST.get('inputPassword5')
        confirm_password = request.POST.get('inputPassword6')
        if new_password and new_password == confirm_password:
            user.set_password(new_password)

        user.save()
        return redirect('/')

    # Determine the base template based on user role
    if is_sales:
        base_template = 'sales_base.html'
    elif is_super_admin:
        base_template = 'base.html'
    else:
        base_template = 'sales_base.html'

    context = {
        'user': user,
        'base_template': base_template,
    }
    return render(request, 'base/profile_setting.html', context)


# def profile_settings(request):
#     user = request.user

#     if request.method == 'POST':
#         # Update the user fields
#         user.first_name = request.POST.get('firstname', '')
#         user.last_name = request.POST.get('lastname', '')
#         user.email = request.POST.get('inputEmail4', '')
#         # Update other fields as needed

#         # Check if the password fields are provided and match
#         new_password = request.POST.get('inputPassword5')
#         confirm_password = request.POST.get('inputPassword6')
#         if new_password and new_password == confirm_password:
#             user.set_password(new_password)

#         user.save()
#         return redirect('profile_settings')


#     return render(request, 'base/profile_setting.html', {'user': user})

# def sendemail(request):
#     user_id = request.GET.get('user_id')  # Get the user_id from the query parameters
#     user = User.objects.get(id=user_id)  # Retrieve the user based on the user_id

#     subject = 'Login Details'
#     html_message = render_to_string('base/email_template.html', {'user': user})
#     plain_message = strip_tags(html_message)
#     from_email = 'your-email@gmail.com'
#     to_email = user.email
#     send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

#     return render(request, 'base/sendemail.html')


from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse

from django.db.models import Q
#after making the list of the user avaliable for every week

def fetch_price_data(request):
    # Get the week offset from the request (0 for this week, -1 for the previous week, etc.)
    week_offset = int(request.GET.get('week_offset', 0))
    
    today = datetime.now(timezone.utc).date()
    # Calculate the start and end dates of the requested week
    start_of_week = (today - timedelta(days=today.weekday())) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get all users
    all_users = User.objects.all()
    
    user_prices = (
        PriceEntry.objects.filter(entry_date__range=(start_of_week, end_of_week))
        .values('user', 'entry_date', 'user__username')
        .annotate(daily_price=Sum('price'))
        .order_by('user', 'entry_date')
    )

    user_price_data = {}
    for user in all_users:
        user_id = user.id
        username = user.username
        user_price_data[user_id] = {'username': username, 'prices': {}}
    
    for entry in user_prices:
        user_id = entry['user']
        entry_date = entry['entry_date'].strftime('%A')
        daily_price = entry['daily_price']

        user_price_data[user_id]['prices'][entry_date] = daily_price

    return JsonResponse(user_price_data)

#after adding css
# def fetch_price_data(request):
#     # Get the week offset from the request (0 for this week, -1 for the previous week, etc.)
#     week_offset = int(request.GET.get('week_offset', 0))
    
#     today = datetime.now(timezone.utc).date()
#     # Calculate the start and end dates of the requested week
#     start_of_week = (today - timedelta(days=today.weekday())) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)
    
#     user_prices = (
#         PriceEntry.objects.filter(entry_date__range=(start_of_week, end_of_week))
#         .values('user', 'entry_date', 'user__username')
#         .annotate(daily_price=Sum('price'))
#         .order_by('user', 'entry_date')
#     )

#     user_price_data = {}
#     for entry in user_prices:
#         user_id = entry['user']
#         username = entry['user__username']
#         entry_date = entry['entry_date'].strftime('%A')
#         daily_price = entry['daily_price']

#         if user_id not in user_price_data:
#             user_price_data[user_id] = {'username': username, 'prices': {}}
#         user_price_data[user_id]['prices'][entry_date] = daily_price

#     return JsonResponse(user_price_data)


#old before adding css
# def fetch_price_data(request):
#     today = datetime.now(timezone.utc).date() #datetime.date.today()
#     start_of_week = today - timedelta(days=today.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#     user_prices = (
#         PriceEntry.objects.filter(entry_date__range=(start_of_week, end_of_week))
#         .values('user', 'entry_date', 'user__username')
#         .annotate(daily_price=Sum('price'))
#         .order_by('user', 'entry_date')
#     )

#     user_price_data = {}
#     for entry in user_prices:
#         user_id = entry['user']
#         username = entry['user__username']
#         entry_date = entry['entry_date'].strftime('%A')
#         daily_price = entry['daily_price']

#         if user_id not in user_price_data:
#             user_price_data[user_id] = {'username': username, 'prices': {}}
#         user_price_data[user_id]['prices'][entry_date] = daily_price

#     return JsonResponse(user_price_data)



def activate_user(request, user_id):
    user = get_object_or_404(CustomUserTypes, id=user_id)
    print("*************Activated****************",user)
    user.is_active = True
    print("==========T  R  UR ==========",user.is_active)
    user.save()
    return JsonResponse({'success': True})

def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUserTypes, id=user_id)
    print("--------DeAvtivated-------",user)
    user.is_active = False
    print("=========F   ALL SE  ===========",user.is_active)
    user.save()
    return JsonResponse({'success': True})


from django.http import JsonResponse
from accounts.models import CustomUserTypes  # Assuming your custom user model is in 'accounts.models'

def toggle_user(request, user_id):
    try:
        user = CustomUserTypes.objects.get(pk=user_id)  # Replace 'User' with 'CustomUserTypes'
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True})
    except CustomUserTypes.DoesNotExist:  # Replace 'User.DoesNotExist' with 'CustomUserTypes.DoesNotExist'
        return JsonResponse({'success': False})



from django.shortcuts import render
from accounts.models import CustomUserTypes  # Assuming your custom user model is in 'accounts.models'

def deactivate_users(request):
    # Fetch a list of deactivated users using the CustomUserTypes model
    deactivated_users = CustomUserTypes.objects.filter(is_active=False)

    # Your other logic related to the deactivate user page can go here...
    # For example, you might perform additional queries, calculations, etc.

    # Pass the list of deactivated users to the template for rendering
    context = {
        'deactivated_users': deactivated_users,
    }

    return render(request, 'base/deactivate_users.html', context)


