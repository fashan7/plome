
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

from leads.models import Lead
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
from datetime import timedelta
from django.utils import timezone
from leads.views import sales_lead


@require_POST
def clear_all_notifications(request):
    user = request.user
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    return JsonResponse({'success': True})

def all_notifications(request):
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
        Notification.objects.filter(user=user, is_read=False) #, timestamp__range=(start_time, end_time)
        .annotate(hour=Trunc('timestamp', 'hour'))
        .values('hour')
        .annotate(count=Count('id'))
        .values('hour', 'count', 'message', 'timestamp', 'id')
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

# @login_required
def admin_dashboard(request):
    if request.user.is_authenticated:
        filtered_user = CustomUserTypes.objects.filter(username=request.user)
        return render(request, 'base/admin_dashboard.html', locals())
    else:
        return render(request, '/login')
    

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


def advisor_dashboard(request):
    return render(request, 'base/advisor_dashboard.html')


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


def sendemail(request):
    user_id = request.GET.get('user_id')  # Get the user_id from the query parameters
    user = User.objects.get(id=user_id)  # Retrieve the user based on the user_id

    subject = 'Login Details'
    html_message = render_to_string('base/email_template.html', {'user': user})
    plain_message = strip_tags(html_message)
    from_email = 'your-email@gmail.com'
    to_email = user.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return render(request, 'base/sendemail.html')


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


def profile_settings(request):
    user = request.user

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
        return redirect('profile')


    return render(request, 'base/profile_setting.html', {'user': user})

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