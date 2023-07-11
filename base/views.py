
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import CustomUserTypes
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

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

        except Exception as e:
            messages.error(request, "An error occurred while saving the user.")
            # Log the error or perform any other necessary actions
            return redirect('add_new_user')
    return redirect('add_new_user')


def advisor_dashboard(request):
    return render(request, 'base/advisor_dashboard.html')
def sales_dashboard(request):
    return render(request, 'base/sales_dashboard.html')
def sadmin_dashboard(request):
    return render(request, 'base/sadmin_dashboard.html')



User = get_user_model()

from django.http import JsonResponse



def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Update the user fields
        user.username = request.POST['Username']
        user.email = request.POST['Email']
        user.first_name = request.POST['firstname']
        user.last_name = request.POST['lastname']
        user.is_sales = request.POST.get('user_type') == 'Sales'
        user.is_advisor = request.POST.get('user_type') == 'Advisor'
        user.is_admin = request.POST.get('user_type') == 'Admin'
        user.save()

        return JsonResponse({'success': True})

    return render(request, 'base/edit_user.html', {'user': user})




def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Delete the user
        user.delete()

        return JsonResponse({'message': 'User deleted successfully.'})

    return JsonResponse({'error': 'Invalid request.'})

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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