# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from django.contrib.auth.models import User
from django.contrib import messages
from accounts.EmailBackEnd import EmailBackEnd
from .models import CustomUserTypes
from django.contrib.auth import logout
from django.http import HttpResponse,HttpResponseNotAllowed
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('signin') 


def redirect_user_dashboard(user):
    if user.is_superuser:
        return redirect('lead/admin_dashboard')
    elif user.is_sales:
        return redirect('lead/sales_dashboard')
    elif user.is_advisor:
        return redirect('base/advisor_dashboard')
    elif user.is_admin:
        return redirect('base/sadmin_dashboard')
    

def redirect_link_dashboard(user):
    if user.is_superuser:
        return 'lead/admin_dashboard'
    elif user.is_sales:
        return 'lead/sales_dashboard'
    elif user.is_advisor:
        return 'base/advisor_dashboard'
    elif user.is_admin:
        return 'base/sadmin_dashboard'


def signin__(request):
    if request.user.is_authenticated:
        # User is already signed in, redirect to their respective page
        user = request.user
        return redirect_user_dashboard(user)

    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = EmailBackEnd.authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print('\n Login Success \n ')
            return redirect_user_dashboard(user)
        else:
            # Invalid credentials, display an error message
            error_message = 'Invalid username or password'
            print(' \n Invalid username or password \n ')
            return render(request, 'accounts/auth-login.html', {'error_message': error_message})
    else:
        # Render the sign-in form
        return render(request, 'accounts/auth-login.html')
    

def signin(request):
    if request.user.is_authenticated:
        # User is already signed in, redirect to their respective page
        user = request.user
        return redirect_user_dashboard(user)
    
    return render(request, 'accounts/auth-login.html')
    



def login_request(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = EmailBackEnd.authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Authenticate and log in the user
            return HttpResponse(redirect_link_dashboard(user)) 
        else:
            return HttpResponse('notok') 
    else:

        return HttpResponseNotAllowed(['POST'])
   

def signup(request):
    if request.method == 'POST':
        
        email = request.POST['Email']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        username = request.POST['Username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            try:
                user = CustomUserTypes.objects.create_superuser(email=email,first_name=first_name,last_name=last_name, username=username, password=password)
                # messages.success(request, 'Superuser account created successfully.')
                print(' \n Superuser account created successfully. \n ')
                return redirect('/')
            except Exception as e:
                print(e)
                # messages.error(request, 'Failed to create superuser account.')
                print(' \n Failed to create superuser account. \n ')
        else:
            print(' \n Passwords do not match. \n ')
            # messages.error(request, 'Passwords do not match.')
    
    return render(request, 'accounts/auth-register.html')


def signout(request):
    logout(request)
    return redirect('/')
# def signout(request):
#     logout(request)
#     return render(request,'accounts/auth-login.html')
