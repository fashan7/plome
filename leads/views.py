from django.contrib.auth.models import User
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from datetime import datetime, timezone, timedelta
import csv
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import CustomUserTypes
from pagesallocation.views import navigation_data
import os
import importlib.util
from .models import Lead, Notification
import json
import pandas as pd
from dateutil.parser import parse as dateutil_parse
import math
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Lead,PriceEntry

from dateutil import parser


def assign_user_to_lead(lead, user_id):
    assigned_user = CustomUserTypes.objects.get(id=user_id)
    lead.assigned_to = assigned_user
    lead.save()
      #Increment the lead count for the assigned user
    assigned_user.lead_count += 1
    assigned_user.save()


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Lead
from . import models

# Custom function to check if the user is a superuser
def is_superuser(user):
    return user.is_superuser

# Decorator to restrict access to the view for non-superusers
@login_required
@user_passes_test(is_superuser, login_url='sales_dashboard')
def admin_dashboard(request):
    # Count all leads
    all_leads_count = Lead.objects.count()

    # Count the leads with the "Signé CPF" qualification
    signe_cpf_leads_count = Lead.objects.filter(qualification='signe_cpf').count()
    conversion_rate = (signe_cpf_leads_count / all_leads_count) * 100 if all_leads_count != 0 else 0

    context = {
        'all_leads_count': all_leads_count,
        'signe_cpf_leads_count': signe_cpf_leads_count, 
        'conversion_rate': conversion_rate, # Add the count for "Signé CPF" leads
    }
    return render(request, 'base/admin_dashboard.html', context)

@login_required
def sales_dashboard(request):
    user = request.user
    # Calculate assigned leads count for non-superusers
    assigned_leads_count = 0
    if not user.is_superuser:
        assigned_leads_count = Lead.objects.filter(assigned_to=user).count()

    # For non-admin users, count leads with the "Signé CPF" qualification assigned to the user
    signe_cpf_leads_count = Lead.objects.filter(qualification='signe_cpf', assigned_to=user).count()
    conversion_rate = (signe_cpf_leads_count / assigned_leads_count) * 100 if assigned_leads_count != 0 else 0

    context = {
        'assigned_leads_count': assigned_leads_count,
        'signe_cpf_leads_count': signe_cpf_leads_count,
        'conversion_rate': conversion_rate, # Add the count for "Signé CPF" leads
    }
    
    return render(request, 'base/sales_dashboard.html', context)




def delete_duplicate_leads():
    # Get all leads ordered by id (to keep the latest lead for each unique telephone number and email)
    all_leads = Lead.objects.order_by('id')

    # Create sets to store unique telephone numbers and email addresses
    unique_telephones = set()
    unique_emails = set()

    duplicates_count = 0

    # Iterate through all leads
    for lead in all_leads:
        # Check if the telephone number is already in the set
        if lead.telephone in unique_telephones and lead.telephone is not None:
            # Delete the duplicate lead
            lead.delete()
            duplicates_count += 1
        else:
            # If the telephone number is not in the set, add it to the set
            unique_telephones.add(lead.telephone)

        # Check if the email address is already in the set
        if lead.email in unique_emails and lead.email is not None:
            # Delete the duplicate lead
            lead.delete()
            duplicates_count += 1
        else:
            # If the email address is not in the set, add it to the set
            unique_emails.add(lead.email)

    return duplicates_count


# #deleting the duplicates only if there numbers are same
# def delete_duplicate_leads():
#     # Get all leads ordered by id (to keep the latest lead for each unique telephone number)
#     all_leads = Lead.objects.order_by('id')

#     # Create a set to store unique telephone numbers
#     unique_telephones = set()

#     duplicates_count = 0

#     # Iterate through all leads
#     for lead in all_leads:
#         # Check if the telephone number is already in the set
#         if lead.telephone in unique_telephones and lead.telephone is not None:
#             # Delete the duplicate lead
#             lead.delete()
#             duplicates_count += 1
#         else:
#             # If the telephone number is not in the set, add it to the set
#             unique_telephones.add(lead.telephone)

#     return duplicates_count



from .models import Notification

from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Lead, CustomUserTypes

@login_required
def filtered_lead_dashboard(request, user_id):
    # Fetch active leads for the selected user
    active_leads = Lead.objects.filter(is_active=True, assigned_to__id=user_id).order_by('-date_de_soumission')
    users = CustomUserTypes.objects.all()
    nav_data = navigation_data(request.user.id)

    return render(request, 'lead/leads_dashboard.html', {'leads': active_leads, 'users': users, 'sections': nav_data})


from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Lead, CustomUserTypes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

@login_required
def lead_dashboard(request, lead_id=None):
    if request.method == 'POST':
        # Retrieve form data and create a new lead instance
        lead = Lead(
            date_de_soumission=request.POST['date_de_soumission'],
            nom_de_la_campagne=request.POST['nom_de_la_campagne'],
            avez_vous_travaille=request.POST['avez_vous_travaille'],
            nom_prenom=request.POST['nom_prenom'],
            telephone=request.POST['telephone'],
            email=request.POST['email'],
            qualification=request.POST['qualification'],
            comments=request.POST['comments']
        )
        custom_field_names = request.POST.getlist('custom_field_name[]')
        custom_field_values = request.POST.getlist('custom_field_value[]')
        custom_fields = dict(zip(custom_field_names, custom_field_values))
        lead.custom_fields = json.dumps(custom_fields)
        
        lead.save()

        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            assigned_user = CustomUserTypes.objects.get(id=assigned_to_id)
            lead.assigned_to = assigned_user
            lead.save()
           
            notification_message = f'You have been assigned a new lead: {lead.nom_de_la_campagne}'

            url = reverse('filtered_lead_dashboard', args=[assigned_user.id])
            url_with_notification = f'{url}?notification={notification_message}'
    
            
            return HttpResponseRedirect(url_with_notification)
        else:
            return redirect('lead_dashboard')
    else:
        # Fetch active leads
        active_leads = Lead.objects.filter(is_active=True).order_by('-date_de_soumission')
        users = CustomUserTypes.objects.all()
        nav_data = navigation_data(request.user.id)


        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            assigned_user = CustomUserTypes.objects.get(id=assigned_to_id)

            notification = Notification(user=assigned_user, lead=lead, message=notification_message)
            notification.save()


        # Check if the user selected a specific user filter
        selected_user_id = request.GET.get('user_id')
        selected_qualification = request.GET.get('qualification')


        page_names = FacebookPage.objects.values_list('page_name', flat=True).distinct()

        if selected_user_id:
            try:
                selected_user = CustomUserTypes.objects.get(id=selected_user_id)
                # Filter leads based on the selected user
                filtered_leads = active_leads.filter(assigned_to__id=selected_user.id)
            except CustomUserTypes.DoesNotExist:
                # If the selected user does not exist, show all active leads
                filtered_leads = active_leads
        else:
            # If no user filter is selected, show all active leads
            filtered_leads = active_leads

        # Apply the qualification filter
        if selected_qualification:
            filtered_leads = filtered_leads.filter(qualification=selected_qualification)
        
        duplicates_deleted = delete_duplicate_leads()
        messages.success(request, f'{duplicates_deleted} duplicate leads deleted.')
        if lead_id is not None:
            lead = get_object_or_404(Lead, id=lead_id)
        else:
            pass



        # Check if the user applied the page name filter
        selected_page_name = request.GET.get('page_name')
        if selected_page_name:
            filtered_leads = filtered_leads.filter(facebook_page__page_name=selected_page_name)

        return render(request, 'lead/leads_dashboard.html', {'leads': filtered_leads, 'users': users, 'sections': nav_data,'page_names': page_names})



#this function is used for history of mention 
from .models import *

@login_required
def lead_history_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead_history = LeadHistory.objects.filter(lead=lead, category='mention').order_by('-timestamp')[:10]
    return render(request, 'lead/lead_history.html', {'lead': lead, 'history_entries': lead_history})

@login_required
def lead_otherhistory_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead_history = LeadHistory.objects.filter(Q(lead=lead, category='other') | Q(lead=lead, category='assign')).order_by('-timestamp')[:10]
    return render(request, 'lead/lead_otherhistory.html', {'lead': lead, 'history_entries': lead_history})


@login_required
def lead_list(request):
    leads = Lead.objects.all()
    return render(request, 'lead/lead_list.html', {'leads': leads})

@login_required
def lead_history(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    history_entries = LeadHistory.objects.filter(lead=lead, category='mention')
    return render(request, 'lead/lead_history.html', {'lead': lead, 'history_entries': history_entries})




from datetime import datetime, timedelta
from django.core.mail import send_mail
import pytz
from .models import Lead
from django.conf import settings

def save_appointment(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')

        lead = Lead.objects.get(pk=lead_id)
        appointment_datetime = datetime.combine(
            datetime.strptime(appointment_date, '%Y-%m-%d').date(),
            datetime.strptime(appointment_time, '%H:%M').time()
        )

        # Convert to timezone-aware datetime using pytz (Europe/Paris timezone)
        tz = pytz.timezone("Europe/Paris")
        appointment_datetime = tz.localize(appointment_datetime)
        
        time_difference = timedelta(minutes=15)
        
        # Calculate reminder timestamp in Europe/Paris timezone
        reminder_datetime = appointment_datetime - time_difference
        print(reminder_datetime)

        # Save the appointment and reminder timestamps
        lead.appointment_date_time = appointment_datetime
        lead.reminder_timestamp = reminder_datetime
        lead.save()

        send_mail(
            'Appointment Scheduled',
            # need to add the user name
            f'Your appointment is scheduled on {lead.appointment_date_time}. ',
            'sender@example.com',
            [lead.email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})



from datetime import timedelta
from django.core.mail import send_mail
import pytz
from .models import Lead
from django.conf import settings
import time

def send_reminder_emails():
    # Create the timezone object
    tz_europe_paris = pytz.timezone("Europe/Paris")

    while True:
        now = datetime.now(pytz.utc)  # Get the current time in UTC

        leads_to_remind = Lead.objects.filter(
            reminder_timestamp__lte=now,
            is_complete=False,
            is_active=True,
            reminder_sent=False,
        )

        for lead in leads_to_remind:
            # Convert lead's reminder timestamp to Europe/Paris timezone using pytz
            reminder_datetime_utc = lead.reminder_timestamp.astimezone(pytz.utc)
            reminder_datetime_paris = reminder_datetime_utc.astimezone(tz_europe_paris)
            
            local_now = now.astimezone(tz_europe_paris)

            if reminder_datetime_paris <= local_now:
                # Send reminder email
                subject = 'Reminder: Your Appointment'
                message = f"Don't forget, you have an appointment at {lead.appointment_date_time}."
                sender_email = settings.EMAIL_HOST_USER
                receiver_email = lead.email

                send_mail(subject, message, sender_email, [receiver_email], fail_silently=False)

                # Mark the reminder as sent
                lead.reminder_sent = True
                lead.save()

       
import threading
reminder_thread = threading.Thread(target=send_reminder_emails)
reminder_thread.daemon = True
reminder_thread.start()
# def save_appointment(request):
#     if request.method == 'POST':
#         lead_id = request.POST.get('lead_id')
#         appointment_date = request.POST.get('appointment_date')
#         appointment_time = request.POST.get('appointment_time')

#         lead = Lead.objects.get(pk=lead_id)
#         lead.appointment_date_time = datetime.combine(
#             datetime.strptime(appointment_date, '%Y-%m-%d').date(),
#             datetime.strptime(appointment_time, '%H:%M').time()
#         )
#         lead.price = None 
#         lead.save()

#         LeadHistory.objects.create(
#             user=request.user,
#             lead=lead,
#             changes=f'{request.user.username} has made an appointment on {appointment_date} @ {appointment_time}',
#             category='other'
#         )
        
#         send_mail(
#             'Appointment Scheduled',
#             f'Your appointment is scheduled on {lead.appointment_date_time}. ', #need to add the user name 
#             'sender@example.com',
#             [lead.email],
#             fail_silently=False,
#         )
        
        
        
#         return JsonResponse({'success': True})
        
#     return JsonResponse({'success': False})

def save_signe_cpf(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        price = request.POST.get('price')

        try:
            lead = Lead.objects.get(id=lead_id)
            lead.price = price
            lead.appointment_date_time = None 
            lead.save()

            PriceEntry.objects.create(user=request.user, price=price, lead=lead)
            LeadHistory.objects.create(
                user=request.user,
                lead=lead,
                changes=f'{request.user.username} has added the Price of {price}',
                category='other'
            )
            return JsonResponse({'success': True})
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_qualification_data(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        selectedValue = request.POST.get('selectedValue')
        try:
            lead = Lead.objects.get(id=lead_id)
            result = None
            if selectedValue == 'rappel':
                result = lead.appointment_date_time
            else:
                result = lead.price

            return JsonResponse({'result': result})
        except Lead.DoesNotExist:
            return JsonResponse({'result': False, 'error': 'Lead not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def view_notifications(request):
    user = request.user
    is_sales = user.groups.filter(name='Sales').exists()  # Assuming Sales group exists for sales users
    is_superuser = user.is_superuser

    # Fetch notifications for the current user
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')

    # Determine the base template based on user role
    if is_sales:
        base_template = 'sales_base.html'
    elif is_superuser:
        base_template = 'base.html'
    else:
        base_template = 'sales_base.html'

    context = {
        'notifications': notifications,
        'base_template': base_template,
    }
    return render(request, 'lead/notification.html', context)

# def lead_dashboard(request):
#     if request.method == 'POST':
#         # Retrieve form data and create a new lead instance
#         lead = Lead(
#             date_de_soumission=request.POST['date_de_soumission'],
#             nom_de_la_campagne=request.POST['nom_de_la_campagne'],
#             avez_vous_travaille=request.POST['avez_vous_travaille'],
#             nom_prenom=request.POST['nom_prenom'],
#             # prenom=request.POST['prenom'],
#             telephone=request.POST['telephone'],
#             email=request.POST['email'],
#             qualification=request.POST['qualification'],
#             comments=request.POST['comments']
#         )
#         lead.save()

#         assigned_to_id = request.POST.get('assigned_to')
#         if assigned_to_id:
#             assigned_user = CustomUserTypes.objects.get(id=assigned_to_id)
#             lead.assigned_to = assigned_user
#             lead.save()
#         duplicates_deleted = delete_duplicate_leads()
#         messages.success(request, f'{lead.nom_de_la_campagne} leads added successfully. {duplicates_deleted} duplicate leads deleted.')
#         return redirect('lead_dashboard')

#     # Fetch active leads
#     active_leads = Lead.objects.filter(is_active=True).order_by('-date_de_soumission')
#     users = CustomUserTypes.objects.all()
#     ##fashan------------------------------------
#     nav_data = navigation_data(request.user.id)


#     return render(request, 'lead/leads_dashboard.html', {'leads': active_leads, 'users': users,'sections': nav_data})

#attachement function which has been used
from django.shortcuts import render, redirect, get_object_or_404
from .models import Lead, Attachment

def attach_file_to_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        attached_file = request.FILES.get('attachment')
        title = request.POST.get('title')  # Retrieve the title from the form data

        if attached_file:
            # Create an Attachment instance and link it to the lead
            attachment = Attachment.objects.create(
                lead=lead,
                file=attached_file,  # Save the file directly, Django handles file storage
                title=title
                # Add other fields for attachment metadata as needed
            )

            return redirect('lead_dashboard', lead_id=lead_id)  # Redirect to the lead detail page or another appropriate view

    return render(request, 'lead/leads_dashboard.html', {'lead': lead})


from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Attachment
from urllib.parse import unquote 

def download_attachment(request, attachment_id, attachment_name):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    
    response = FileResponse(attachment.file, as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{unquote(attachment_name)}"'
    
    return response

from django.http import JsonResponse
    
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    attachment.file.delete()  # Delete the attached file from storage
    attachment.delete()  # Delete the Attachment instance
    return JsonResponse({'message': 'Attachment deleted successfully'})




from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType

def lead_edit(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        form_data = request.POST.copy()  # Make a copy of the POST data to modify it
        assigned_user_id = form_data.get('assigned_to')  # Get the assigned user ID from the form data
        

        if assigned_user_id:
            try:
                assigned_user = CustomUserTypes.objects.get(id=assigned_user_id)
                lead.assigned_to = assigned_user  # Set the assigned user for the lead
            except CustomUserTypes.DoesNotExist:
                # Handle the case when the selected user does not exist (optional)
                messages.error(request, 'Invalid user ID selected for assignment.')

        changes = {}

        # Check if each field has been changed and update the changes dictionary
        if str(lead.date_de_soumission) != form_data['date_de_soumission']:
            changes['Date de soumission'] = form_data['date_de_soumission']

        if lead.avez_vous_travaille != form_data['avez_vous_travaille']:
            changes['avez_vous_travaille'] = form_data['avez_vous_travaille']

        if lead.nom_de_la_campagne != form_data['nom_de_la_campagne']:
            changes['Nom de la campagne'] = form_data['nom_de_la_campagne']
            
        if lead.nom_prenom != form_data['nom_prenom']:
            changes['Nom & Prenom'] = form_data['nom_prenom']
            
        if lead.telephone != form_data['telephone']:
            changes['Telephone'] = form_data['telephone']
        
        if lead.email != form_data['email']:
            changes['Email'] = form_data['email']

        if lead.qualification != form_data['qualification']:
            changes['Qualification'] = form_data['qualification']
            
        if lead.comments != form_data['comments']:
            changes['Comments'] = form_data['comments']

        appointmentDT = form_data.get('appointmentStatDateTime')
        IsdateChange = False
        if lead.appointment_date_time != appointmentDT and lead.appointment_date_time is not None:
            IsdateChange = True

        IspriceChange = False
        if str(lead.price) != str(form_data['price']) and lead.price is not None:
            IspriceChange = True
            changes['Price'] = form_data['price']
            price_entry = PriceEntry.objects.filter(lead=lead, entry_date=datetime.now(timezone.utc).date()).first()
            if price_entry:
                price_entry.price = form_data['price']
                price_entry.save()
            else:
                PriceEntry.objects.create(user=request.user, entry_date=datetime.now(timezone.utc).date(), price=form_data['price'], lead=lead)

        # Repeat the above process for other fields

        # Update the lead instance with the form data
        lead.date_de_soumission = form_data['date_de_soumission']
        lead.nom_de_la_campagne = form_data['nom_de_la_campagne']
        lead.avez_vous_travaille = form_data['avez_vous_travaille']
        lead.nom_prenom = form_data['nom_prenom']
        lead.telephone = form_data['telephone']
        lead.email = form_data['email']
        lead.qualification = form_data['qualification']
        lead.comments = form_data['comments']
        isDateReallyChanged = False
        formatted_datetime = None

        if appointmentDT != 'None' and IsdateChange:
            try:
                formatted_datetime = parser.parse(appointmentDT)
            except Exception as e:
                formatted_datetime = appointmentDT
            if lead.appointment_date_time.strftime('%Y-%m-%d %H:%M:%S') != str(formatted_datetime):
                isDateReallyChanged = True
        elif appointmentDT == 'None' and IsdateChange:
            formatted_datetime = parser.parse(appointmentDT)
            if lead.appointment_date_time.strftime('%Y-%m-%d %H:%M:%S') != str(formatted_datetime):
                isDateReallyChanged = True

        if isDateReallyChanged and formatted_datetime is not None:
            changes['Appointment Date Time'] = form_data['appointmentStatDateTime']
            #Adding the mail for scheduling the appointment, if the user ressheduled the date
            send_mail(
                'Appointment Scheduled',
                f'Your appointment is scheduled on {lead.appointment_date_time}. ', #need to add the user name 
                'sender@example.com',
                [lead.email],
                fail_silently=False,
            )
            
            
            lead.appointment_date_time = formatted_datetime
       
        price = form_data.get('price')
        if price != 'None':
            lead.price = price

        if isDateReallyChanged:
            lead.price = None #if User selects rappel, price will be nulled

        if IspriceChange:
            lead.appointment_date_time = None #if User selects signe_cpf, appointmentdt will be nulled

        if form_data['qualification'] != 'signe_cpf' and form_data['qualification'] != 'rappel':
            lead.appointment_date_time = None
            lead.price = None


        custom_fields_data = {}
        for key, value in form_data.items():
            if key.startswith('custom_fields.'):
                custom_field_key = key.split('.', 1)[1]
                custom_fields_data[custom_field_key] = value
        

        custom_field_names = request.POST.getlist('custom_field_name[]')
        custom_field_values = request.POST.getlist('custom_field_value[]')
        custom_fields_ = dict(zip(custom_field_names, custom_field_values))
        if len(custom_fields_) > 0:
            custom_fields_data.update(custom_fields_)
            lead.custom_fields = json.dumps(custom_fields_data)
        else:
            lead.custom_fields = json.dumps(custom_fields_data)

        # Set the last_modified_by field to the current user
        lead.last_modified_by = request.user

        lead.save()


        #Saving the notification for assign
        if assigned_user_id:
            notification_message = f'You have been assigned a new lead: {lead.nom_de_la_campagne}'
            user = CustomUserTypes.objects.get(id=assigned_user_id)
            notification = Notification(user=user, lead=lead, message=notification_message)
            notification.save()
        messages.success(request, 'Lead edited successfully.')

        # Create a LogEntry to track the change made by the user
        content_type = ContentType.objects.get_for_model(Lead)
        username = request.user.username
        change_message = f'{username} edited the Lead. Changes: {", ".join([f"{field}: {value}" for field, value in changes.items()])}'
        log_entry = LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=content_type.id,
            object_id=lead.id,
            object_repr=f'{lead}',
            action_flag=CHANGE,
            change_message=change_message
        )

        LeadHistory.objects.create(
            user=request.user,
            lead=lead,
            changes=change_message,
            category='other'
        )

        context = {
            'lead': lead,
            'change_message': change_message,
            'log_entry': log_entry,
        }
        return JsonResponse({'success': True})

    return render(request, 'lead/lead_edit.html', {'lead': lead})

from django.http import JsonResponse
from .models import PriceEntry

def get_latest_price_entry(request):
    latest_entry = PriceEntry.objects.latest('entry_date')
    entry_data = {
        'user': latest_entry.user.username,
        'price': str(latest_entry.price),
    }
    return JsonResponse(entry_data)


from django.http import JsonResponse

def save_custom_field(request, lead_id):
    if request.method == 'POST':
        lead = get_object_or_404(Lead, id=lead_id)
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')

        # Update custom_fields data and save the lead
        custom_fields_data = json.loads(lead.custom_fields)
        custom_fields_data[field_name] = field_value
        lead.custom_fields = json.dumps(custom_fields_data)
        lead.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_count(request):
    unread_notification_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return  {'unread_notification_count': unread_notification_count}


#can be used in future 

# def lead_edit(request, lead_id):
#     lead = get_object_or_404(Lead, id=lead_id)

#     if request.method == 'POST':
#         form_data = request.POST.copy()  # Make a copy of the POST data to modify it
#         assigned_user_id = form_data.get('assigned_to')  # Get the assigned user ID from the form data

#         if assigned_user_id:
#             try:
#                 assigned_user = CustomUserTypes.objects.get(id=assigned_user_id)
#                 lead.assigned_to = assigned_user  # Set the assigned user for the lead
#             except CustomUserTypes.DoesNotExist:
#                 # Handle the case when the selected user does not exist (optional)
#                 messages.error(request, 'Invalid user ID selected for assignment.')

#         # Update the lead instance with the form data
#         lead.date_de_soumission = form_data['date_de_soumission']
#         lead.nom_de_la_campagne = form_data['nom_de_la_campagne']
#         lead.avez_vous_travaille = form_data['avez_vous_travaille']
#         lead.nom_prenom = form_data['nom_prenom']
#         lead.telephone = form_data['telephone']
#         lead.email = form_data['email']
#         lead.qualification = form_data['qualification']
#         lead.comments = form_data['comments']

#         # Save the lead instance to the database
#         lead.save()
#         messages.success(request, 'Lead edited successfully.')

#         return JsonResponse({'success': True})

#     return render(request, 'lead/lead_edit.html', {'lead': lead})



def toggle_lead_status(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.is_active = not lead.is_active  # Toggle the status
    lead.save()

    if lead.is_active:
        return redirect('lead_dashboard')
    else:
        return redirect('deactivated_leads')
    
    
def deactivated_leads(request):
    leads = Lead.objects.filter(is_active=False)
    return render(request, 'lead/deactivated_lead.html', {'leads': leads})

@login_required
def toggle_saleslead_status(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.is_complete = not lead.is_complete  # Toggle the status
    lead.save()

    if lead.is_complete:
        return redirect('complete_leads')
    else:
        return redirect('sales_lead')

@login_required
def complete_leads(request):
    leads = Lead.objects.filter(is_complete=True)
    return render(request, 'lead/complete_leads.html', {'leads': leads})





# def parse_date(date_str):
#     try:
#         # Try parsing with format '%Y-%m-%d %H:%M:%S'
#         return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         try:
#             # Try parsing with format '44764,59196'
#             if isinstance(date_str, pd.Timestamp):
#                 date_str = str(date_str)
#             timestamp = float(date_str.replace(',', '.')) * 86400
#             min_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
#             max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

#             # Check if the parsed timestamp is within a reasonable range
#             if min_datetime.timestamp() <= timestamp <= max_datetime.timestamp():
#                 return datetime.fromtimestamp(timestamp)
#             else:
#                 return None
#         except ValueError:
#             return None
        
import csv
import math
import pandas as pd
from datetime import datetime, timezone
from django.contrib import messages
from .models import Lead
from django.db import transaction

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))
    

import pandas as pd
from dateutil.parser import parse as dateutil_parse
import math
import numpy as np


def parse_date_with_format(date_string):
    try:
        # Try parsing with format '%m/%d/%Y %H:%M'
        date_obj = datetime.strptime(date_string, '%m/%d/%Y %H:%M')
        return date_obj
    except ValueError:
        try:
            # Try parsing with format '%Y-%m-%d %H:%M:%S'
            date_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return date_obj
        except ValueError:
            try:
                # Try parsing with format '%m/%d/%Y %H:%M:%S'
                date_obj = datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
                return date_obj
            except ValueError:
                # If none of the formats match, return None
                return None
        return None
    

def parse_date(date_string):
    try:
        # Try using dateutil.parser.parse to automatically parse the date
        if isinstance(date_string, float):
            return datetime.now()
        
        if date_string:
            date_obj = dateutil_parse(date_string)
            return date_obj
        else:
            return datetime.now()
    except ValueError:
        return None






def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))


def import_leads(request):
    field_map = {
        'date_de_soumission': 'date de soumission',
        'nom_de_la_campagne': 'nom de la campagne',
        'avez_vous_travaille': 'avez vous travaillé ?',
        'nom_prenom': 'nom et prénom',
        'telephone': 'téléphone',
        'email': 'e-mail',
        'qualification': 'qualification',
        'comments': 'commentaires',
    }
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    raise ValueError("Unsupported file format. Only CSV, XLS, and XLSX files are allowed.")

                headers = [header.strip() for header in df.columns]
                field_map_normalized = {key.lower().replace(" ", "_"): value for key, value in field_map.items()}  # Normalize field_map keys
                filtered_headers = [header for header in headers if header.lower() in field_map_normalized.values()]
                
                additional_headers = [header for header in headers if header.lower() not in field_map_normalized.values()]
                filtered_headers_lower = [header.lower() for header in filtered_headers]
                filtered_field_map = {key: value for key, value in field_map.items() if value in filtered_headers_lower}

                df_dict = df.to_dict(orient='records')
                json_data = json.dumps(df_dict, default=date_handler)
                request.session['df'] = json_data #df.to_dict(orient='records', date_format='iso', date_unit='s', default_handler=str)
                request.session['field_map'] = field_map
               
                context = {'headers': headers, 'field_map': field_map, 'additional_headers': additional_headers}
                return render(request, 'lead/mapping_modal.html', context)
            except Exception as e:
                messages.error(request, f'Error reading file: {str(e)}')
                return redirect('lead_dashboard')
            
        elif 'mapping' in request.POST:
            mapping_data = {}  
            custom_fields = {}


            for field, field_name in field_map.items():
                mapping_data[field] = request.POST.get(field, '')


            for field, field_name in field_map.items():
                mapping_data[field] = request.POST.get(field, '')

            for custom_field in request.POST.getlist('custom_fields'):
                custom_fields[custom_field] = custom_field

            mapping_data.update({'custom_fields':custom_fields})


            df_records = request.session.get('df', [])
            field_map = request.session.get('field_map', {})
            # print(df_records)
            # print(field_map)
            # print(mapping_data)
            
            leads = []
            for record in json.loads(df_records):
                lead_data = {}
                for header, field in mapping_data.items():
                    if field == '__empty__':
                        value_holder = None  # Skip this field
                    elif header == 'custom_fields':
                        custom_f = {}
                        for excess_key, excess_fields in field.items():
                            excess_value = record.get(excess_key)
                            excess_value_holder = None
                            if (isinstance(excess_value, float) and math.isnan(excess_value)) or excess_value == 'NaT':
                                excess_value_holder = ''
                            else:
                                excess_value_holder =  excess_value
                            custom_f[excess_key] = excess_value_holder
                        lead_data['custom_fields'] = custom_f
                    else:
                        value = record.get(field)
                        value_holder = None
                        if header == 'date_de_soumission':
                            date_de_soumission = parse_date(value)
                            value_holder = date_de_soumission
                        elif isinstance(value, float) and math.isnan(value):
                            value_holder = ' '
                        elif isinstance(value, float) and not math.isnan(value):
                            value_holder = int(value) if value.is_integer() else value
                        else:
                            value_holder = record[field]
                        
                        lead_data[header] = value_holder
                leads.append(Lead(**lead_data))
            print(len(leads))
            Lead.objects.bulk_create(leads)
            request.session.pop('df', None)
            request.session.pop('field_map', None)

            duplicates_deleted = delete_duplicate_leads()
            messages.success(request, f'{len(leads)} leads imported successfully. {duplicates_deleted} duplicate leads deleted.')

            return redirect('lead_dashboard')
            
    return redirect('lead_dashboard')


def delete_leads(request):
    if request.method == 'POST' and request.is_ajax():
        lead_ids = request.POST.getlist('lead_ids[]')
        Lead.objects.filter(id__in=lead_ids).delete()
        return JsonResponse({'success': True, 'message': 'Selected leads deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


import csv
import pandas as pd
from django.http import HttpResponse

def export_leads(request, file_format):
    if file_format not in ('csv', 'xlsx'):
        return HttpResponse("Invalid file format specified.", status=400)

    leads = Lead.objects.all()

    if file_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'
        writer = csv.writer(response)

        # Write header row
        writer.writerow([
            'Date de Soumission',
            'Nom de la Campagne',
            'Avez-vous travaillé',
            'Nom & Prenom',
            'Téléphone',
            'Email',
            'Qualification',
            'Comments',
        ])

        # Write data rows
        for lead in leads:
            writer.writerow([
                lead.date_de_soumission,
                lead.nom_de_la_campagne,
                lead.avez_vous_travaille,
                lead.nom_prenom,
                lead.telephone,
                lead.email,
                lead.qualification,
                lead.comments,
            ])

    elif file_format == 'xlsx':
        df = pd.DataFrame(list(leads.values(
            'date_de_soumission',
            'nom_de_la_campagne',
            'avez_vous_travaille',
            'nom_prenom',
            'telephone',
            'email',
            'qualification',
            'comments',
        )))

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="leads.xlsx"'
        df.to_excel(response, index=False)

    return response



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render
from django.db.models import Q  # Import Q for complex queries
from .models import FacebookPage, Lead  # Import the necessary models


from django.http import JsonResponse
from django.shortcuts import render
from .models import FacebookPage, Lead
import facebook

# @login_required
# def sales_lead(request):
#     qualification_filter = request.GET.get('qualification')

#     # Filter the list of Facebook pages based on the currently logged-in user
#     user_facebook_pages = FacebookPage.objects.filter(user=request.user)

#     # Get leads associated with the user's Facebook pages
#     user_leads = Lead.objects.filter(
#         Q(assigned_to=request.user) | Q(transfer_to=request.user),
#         facebook_page__in=user_facebook_pages,  # Filter by the user's Facebook pages
#         is_active=True,
#         is_complete=False
#     )

#     if qualification_filter:
#         user_leads = user_leads.filter(qualification=qualification_filter)

#     # Fetch Facebook leads here
#     response_data = fetch_sales_leads(request)

#     # You can access data fetched by fetch_facebook_leads through the 'response_data' dictionary
#     fetched_message = response_data.get('message', '')  # Access the 'message' key

#     return render(request, 'lead/sales_lead.html', {'leads': user_leads, 'fetched_message': fetched_message, 'page_names': user_facebook_pages})




# @login_required
# def sales_lead(request):    
#     qualification_filter = request.GET.get('qualification')
#     fetch_sales_leads(request)
    
#     # Filter the list of Facebook pages based on the currently logged-in user
#     user_facebook_pages = FacebookPage.objects.filter(user=request.user)
    
#     # Get leads associated with the user's Facebook pages
#     user_leads = Lead.objects.filter(
#         Q(assigned_to=request.user) | Q(transfer_to=request.user),
#         facebook_page__in=user_facebook_pages,  # Filter by the user's Facebook pages
#         is_active=True,
#         is_complete=False
#     )
    
#     if qualification_filter:
#         user_leads = user_leads.filter(qualification=qualification_filter)
        
    
#     return render(request, 'lead/sales_lead.html',{'leads': user_leads, 'page_names': user_facebook_pages})


# @login_required
# def sales_lead(request):    
#     qualification_filter = request.GET.get('qualification')
#     user_leads = Lead.objects.filter(Q(assigned_to=request.user) | Q(transfer_to=request.user), is_active=True, is_complete=False)
#     if qualification_filter:
#         user_leads = user_leads.filter(qualification=qualification_filter)
#     return render(request, 'lead/sales_lead.html', {'leads': user_leads})


def assign_leads(request):
    if request.method == 'POST':
        selected_leads = request.POST.get('selected_leads')
        assign_to_user_id = request.POST.get('assign_to_user')
        if not selected_leads or not assign_to_user_id:
            return JsonResponse({'success': False, 'message': 'Invalid data.'}, status=400)

        try:
            assigned_user = CustomUserTypes.objects.get(id=assign_to_user_id)
        except CustomUserTypes.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Assigned user not found.'}, status=400)

        try:
            selected_leads = json.loads(selected_leads)
            for lead_data in selected_leads:
                lead_id = lead_data.get('id')

                lead = Lead.objects.get(id=lead_id)
                lead.assigned_to = assigned_user
                lead.save()

                notification_message = f'You have been assigned a new lead: {lead.nom_de_la_campagne}'
                notification = Notification(user=assigned_user, lead=lead, message=notification_message)
                notification.save()
                changes = 'Assigned'
                LeadHistory.objects.create(lead=lead, user=request.user,  changes=changes, category='assign')

            return JsonResponse({'success': True, 'message': 'Leads assigned successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)


# views.py
from django.http import HttpResponse
from django.shortcuts import render
from .models import FacebookPage

def save_facebook_form_ids(request):
    if request.method == 'POST' and 'save_facebook_form_ids' in request.POST:
        # Define a list of Facebook form IDs and their associated page names
        form_ids = [
            {'form_id': '1316143499002088', 'page_name': 'Clément'},
            {'form_id': '210879228573885', 'page_name': 'Bruno'},
            {'form_id': '1254659748572732', 'page_name': 'Johanna'},
            {'form_id': '314661597574782', 'page_name': 'Bruno 2'},
            # Add more form IDs and page names as needed
        ]

        for form_data in form_ids:
            form_id = form_data['form_id']
            page_name = form_data['page_name']

            # Create a FacebookPage instance or get an existing one
            facebook_page, created = FacebookPage.objects.get_or_create(form_id=form_id)
            facebook_page.page_name = page_name
            facebook_page.save()

        return HttpResponse("Facebook form IDs and page names saved successfully.")

    return HttpResponse("not saved successfully.")  # Replace 'your_template.html' with your actual template name

import facebook
from django.http import HttpResponse

# views.py



from django.shortcuts import render, redirect
from .models import FacebookPage, token  # Import the Token model

def update_access_token(request):
    if request.method == 'POST':
        page_name = request.POST.get('page_name')
        access_token = request.POST.get('access_token')

        # Create or update the access token in the Token model
        token_instance, created = token.objects.get_or_create()
        token_instance.access_token = access_token
        token_instance.save()

        try:
            # Retrieve the FacebookPage instance
            facebook_page = FacebookPage.objects.get(page_name=page_name)
            # Update the access token
            facebook_page.access_token = access_token
            facebook_page.save()
        except FacebookPage.DoesNotExist:
            pass  # Handle the case where the page doesn't exist

    # Redirect the user to a relevant page (e.g., the page with access token management)
    return redirect('lead_dashboard')



from .models import Lead, FacebookPage  # Import your Lead and FacebookPage models




import csv
import facebook
from django.http import JsonResponse  # Import JsonResponse
from .models import FacebookPage, Lead, token
from django.http import JsonResponse
import facebook
 # Import the Token model



def fetch_facebook_leads(request):
    response_data = {}  # Create a dictionary to store response data

    if request.method == 'POST' and 'fetch_facebook_leads' in request.POST:
        selected_page_name = request.POST.get('page_name')

        try:
            token_instance = token.objects.latest('id')
            access_token = token_instance.access_token
        except token.DoesNotExist:
            response_data['error'] = "Access token not found. Please add an access token."
            return JsonResponse(response_data)

        try:
            # Get the currently logged-in user
            current_user = request.user  # Assumes you are using Django's built-in authentication

            # Retrieve the Facebook pages associated with the current user
            facebook_page = FacebookPage.objects.filter(page_name=selected_page_name, user=current_user).first()

            if not facebook_page:
                response_data['error'] = "Selected Facebook page not found or not mapped to the current user."
                return JsonResponse(response_data)
        except FacebookPage.DoesNotExist:
            response_data['error'] = "Selected Facebook page not found."
            return JsonResponse(response_data)

        try:
            graph = facebook.GraphAPI(access_token=access_token, version="3.0")
        except facebook.GraphAPIError as e:
            response_data['error'] = f"Error connecting to Facebook Graph API: {e}"
            return JsonResponse(response_data)

        leads = []
        cursor = None

        while True:
            try:
                params = {'fields': 'field_data,ad_id', 'limit': 100}
                if cursor:
                    params['after'] = cursor
                response = graph.get_object(f"/{facebook_page.form_id}/leads", **params)
                leads.extend(response['data'])
                if 'paging' in response and 'cursors' in response['paging']:
                    cursor = response['paging']['cursors']['after']
                else:
                    break
            except facebook.GraphAPIError as e:
                response_data['error'] = f"Error retrieving leads: {e}"
                return JsonResponse(response_data)

        for lead in leads:
            name = None
            email = None
            phone = None
            nom_de_la_campagne = None
            avez_vous_travaille = None
            status = None
            date_de_soumission = None  # Initialize date_de_soumission

            for field in lead['field_data']:
                if field['name'] == 'full_name':
                    name = field['values'][0]
                elif field['name'] == 'email':
                    email = field['values'][0]
                elif field['name'] == 'phone_number':
                    phone = field['values'][0]
                elif field['name'] == 'campaign_name':
                    nom_de_la_campagne = field['values'][0]
                elif field['name'] == 'vous_avez_déjà_travaillé_?':
                    avez_vous_travaille = field['values'][0]
                elif field['name'] == 'created_time':
                    date_de_soumission = field['values'][0]

            if 'ad_id' in lead:
                status = 'new'
            else:
                status = 'expired'

            lead_instance = Lead(
                nom_de_la_campagne=nom_de_la_campagne,
                avez_vous_travaille=avez_vous_travaille,
                nom_prenom=name,
                telephone=phone,
                email=email,
                qualification=None,
                comments=None,
                assigned_to=None,
                date_de_soumission=date_de_soumission,
                facebook_page=facebook_page,
                lead_source='facebook',
            )
            lead_instance.save()

        response_data['message'] = "Leads fetched and saved to the database."
        return JsonResponse(response_data)

    response_data['error'] = "No action taken."
    return JsonResponse(response_data)



from django.shortcuts import render, redirect
from .models import FacebookPage, CustomUserTypes  # Import the CustomUserTypes model

def map_facebook_pages_to_users(request):
    if request.method == 'POST':
        # Get the selected page and user from the form submission
        selected_page_id = request.POST.get('selected_page')
        selected_user_id = request.POST.get('selected_user')

        try:
            # Retrieve the selected Facebook Page and User
            selected_page = FacebookPage.objects.get(pk=selected_page_id)
            selected_user = CustomUserTypes.objects.get(pk=selected_user_id)

            # Update the user field for the Facebook Page
            selected_page.user = selected_user
            selected_page.save()

            # Redirect to a success page or display a success message
            return redirect('map_facebook_pages')  # Replace 'success_page' with the actual URL name
        except (FacebookPage.DoesNotExist, CustomUserTypes.DoesNotExist):
            # Handle cases where the selected page or user doesn't exist
            error_message = "Selected Facebook Page or User not found."
            return render(request, 'error_template.html', {'error_message': error_message})

    # If the request method is not POST, or if the form hasn't been submitted
    # Retrieve a list of all Facebook Pages and Users for the template
    facebook_pages = FacebookPage.objects.all()
    users = CustomUserTypes.objects.all()
    return render(request, 'lead/mapping_template.html', {'facebook_pages': facebook_pages, 'users': users})

@login_required
def fetch_sales_leads(request):
    response_data = {}  # Create a dictionary to store response data

    try:
        token_instance = token.objects.latest('id')
        access_token = token_instance.access_token
    except token.DoesNotExist:
        response_data['error'] = "Access token not found. Please add an access token."
        return JsonResponse(response_data)

    try:
        # Get the currently logged-in user
        current_user = request.user  # Assumes you are using Django's built-in authentication

        # Retrieve all the Facebook pages associated with the current user
        user_facebook_pages = FacebookPage.objects.filter(user=current_user)
    except FacebookPage.DoesNotExist:
        response_data['error'] = "No Facebook pages found for the current user."
        return JsonResponse(response_data)

    for facebook_page in user_facebook_pages:
        try:
            graph = facebook.GraphAPI(access_token=access_token, version="3.0")

            leads = []
            cursor = None

            while True:
                try:
                    params = {'fields': 'field_data,ad_id', 'limit': 100}
                    if cursor:
                        params['after'] = cursor
                    response = graph.get_object(f"/{facebook_page.form_id}/leads", **params)
                    leads.extend(response['data'])
                    if 'paging' in response and 'cursors' in response['paging']:
                        cursor = response['paging']['cursors']['after']
                    else:
                        break
                except facebook.GraphAPIError as e:
                    response_data['error'] = f"Error retrieving leads: {e}"
                    return JsonResponse(response_data)

            for lead in leads:
                # Check if the lead's Facebook ID has already been fetched
                facebook_lead_id = lead.get('id')  # Assuming 'id' is the field that stores the Facebook ID
                if not FetchedLead.objects.filter(facebook_lead_id=facebook_lead_id).exists():
                    # This lead is new; fetch and save it

                    # Your lead fetching and saving logic here
                    # For example:
                    name = None
                    email = None
                    phone = None
                    nom_de_la_campagne = None
                    avez_vous_travaille = None
                    status = None
                    date_de_soumission = None  # Initialize date_de_soumission

                    for field in lead['field_data']:
                        if field['name'] == 'full_name':
                            name = field['values'][0]
                        elif field['name'] == 'email':
                            email = field['values'][0]
                        elif field['name'] == 'phone_number':
                            phone = field['values'][0]
                        elif field['name'] == 'campaign_name':
                            nom_de_la_campagne = field['values'][0]
                        elif field['name'] == 'vous_avez_déjà_travaillé_?':
                            avez_vous_travaille = field['values'][0]
                        elif field['name'] == 'created_time':
                            date_de_soumission = field['values'][0]

                    if 'ad_id' in lead:
                        status = 'new'
                    else:
                        status = 'expired'

                    # Assign the lead to the user mapped to the Facebook page
                    assigned_user = facebook_page.user  # Assuming you have a 'user' field in your FacebookPage model

                    lead_instance = Lead(
                        nom_de_la_campagne=nom_de_la_campagne,
                        avez_vous_travaille=avez_vous_travaille,
                        nom_prenom=name,
                        telephone=phone,
                        email=email,
                        qualification=None,
                        comments=None,
                        assigned_to=assigned_user,
                        date_de_soumission=date_de_soumission,
                        facebook_page=facebook_page,
                        lead_source='facebook',
                    )
                    lead_instance.save()

                    # Store the Facebook ID of the fetched lead
                    fetched_lead = FetchedLead(lead=lead_instance, facebook_lead_id=facebook_lead_id)
                    fetched_lead.save()

            response_data['message'] = "Sales Leads fetched and saved to the database."
        except facebook.GraphAPIError as e:
            response_data['error'] = f"Error connecting to Facebook Graph API: {e}"

    return JsonResponse(response_data)

@login_required
def sales_lead(request):
    qualification_filter = request.GET.get('qualification')

    # Filter the list of Facebook pages based on the currently logged-in user
    user_facebook_pages = FacebookPage.objects.filter(user=request.user)

    # Get leads associated with the user's Facebook pages
    user_leads = Lead.objects.filter(
        Q(assigned_to=request.user) | Q(transfer_to=request.user),
        facebook_page__in=user_facebook_pages,  # Filter by the user's Facebook pages
        is_active=True,
        is_complete=False
    )

    if qualification_filter:
        user_leads = user_leads.filter(qualification=qualification_filter)

    # Fetch Facebook leads here
    response_data = fetch_sales_leads(request)

    # You can access data fetched by fetch_sales_leads through the 'response_data' dictionary
    fetched_message = response_data.get('message', '')  # Access the 'message' key

    return render(request, 'lead/sales_lead.html', {'leads': user_leads, 'fetched_message': fetched_message, 'page_names': user_facebook_pages})



# @login_required
# def fetch_sales_leads(request):
#     response_data = {}  # Create a dictionary to store response data

#     if request.method == 'POST' and 'fetch_sales_leads' in request.POST:
#         selected_page_name = request.POST.get('page_name')

#         try:
#             token_instance = token.objects.latest('id')
#             access_token = token_instance.access_token
#         except token.DoesNotExist:
#             response_data['error'] = "Access token not found. Please add an access token."
#             return JsonResponse(response_data)

#         try:
#             # Get the currently logged-in user
#             current_user = request.user  # Assumes you are using Django's built-in authentication

#             # Retrieve the Facebook pages associated with the current user
#             facebook_page = get_object_or_404(FacebookPage, page_name=selected_page_name, user=current_user)

#         except FacebookPage.DoesNotExist:
#             response_data['error'] = "Selected Facebook page not found."
#             return JsonResponse(response_data)

#         try:
#             graph = facebook.GraphAPI(access_token=access_token, version="3.0")
#         except facebook.GraphAPIError as e:
#             response_data['error'] = f"Error connecting to Facebook Graph API: {e}"
#             return JsonResponse(response_data)

#         leads = []
#         cursor = None

#         while True:
#             try:
#                 params = {'fields': 'field_data,ad_id', 'limit': 100}
#                 if cursor:
#                     params['after'] = cursor
#                 response = graph.get_object(f"/{facebook_page.form_id}/leads", **params)
#                 leads.extend(response['data'])
#                 if 'paging' in response and 'cursors' in response['paging']:
#                     cursor = response['paging']['cursors']['after']
#                 else:
#                     break
#             except facebook.GraphAPIError as e:
#                 response_data['error'] = f"Error retrieving leads: {e}"
#                 return JsonResponse(response_data)

#         for lead in leads:
#             # Check if the lead's Facebook ID has already been fetched
#             facebook_lead_id = lead.get('id')  # Assuming 'id' is the field that stores the Facebook ID
#             if not FetchedLead.objects.filter(facebook_lead_id=facebook_lead_id).exists():
#                 # This lead is new; fetch and save it

#                 # Your lead fetching and saving logic here
#                 # For example:
#                 name = None
#                 email = None
#                 phone = None
#                 nom_de_la_campagne = None
#                 avez_vous_travaille = None
#                 status = None
#                 date_de_soumission = None  # Initialize date_de_soumission

#                 for field in lead['field_data']:
#                     if field['name'] == 'full_name':
#                         name = field['values'][0]
#                     elif field['name'] == 'email':
#                         email = field['values'][0]
#                     elif field['name'] == 'phone_number':
#                         phone = field['values'][0]
#                     elif field['name'] == 'campaign_name':
#                         nom_de_la_campagne = field['values'][0]
#                     elif field['name'] == 'vous_avez_déjà_travaillé_?':
#                         avez_vous_travaille = field['values'][0]
#                     elif field['name'] == 'created_time':
#                         date_de_soumission = field['values'][0]

#                 if 'ad_id' in lead:
#                     status = 'new'
#                 else:
#                     status = 'expired'

#                 # Assign the lead to the user mapped to the Facebook page
#                 assigned_user = facebook_page.user  # Assuming you have a 'user' field in your FacebookPage model

#                 lead_instance = Lead(
#                     nom_de_la_campagne=nom_de_la_campagne,
#                     avez_vous_travaille=avez_vous_travaille,
#                     nom_prenom=name,
#                     telephone=phone,
#                     email=email,
#                     qualification=None,
#                     comments=None,
#                     assigned_to=assigned_user,
#                     date_de_soumission=date_de_soumission,
#                     facebook_page=facebook_page,
#                     lead_source='facebook',
#                 )
#                 lead_instance.save()

#                 # Store the Facebook ID of the fetched lead
#                 fetched_lead = FetchedLead(lead=lead_instance, facebook_lead_id=facebook_lead_id)
#                 fetched_lead.save()

#         response_data['message'] = "Sales Leads fetched and saved to the database."
#         return JsonResponse(response_data)

#     response_data['error'] = "No action taken."
#     return JsonResponse(response_data)













# views.py
# from django.http import HttpResponse, HttpResponseRedirect
# from django.urls import reverse
# from .models import FacebookPage, Lead

# from django.shortcuts import render, HttpResponse, redirect
# from django.urls import reverse
# from .models import FacebookPage, Lead
# import facebook

# def fetch_facebook_leads(request):
#     if request.method == 'POST' and 'fetch_facebook_leads' in request.POST:
#         # Get the selected page name from the form
#         selected_page_name = request.POST.get('page_name')

#         # Use the selected page name to fetch the associated form ID
#         try:
#             facebook_page = FacebookPage.objects.get(page_name=selected_page_name)
#             form_id = facebook_page.form_id
#         except FacebookPage.DoesNotExist:
#             return HttpResponse("Selected Facebook page not found.")

#         # Fetch data from Facebook using the retrieved form ID
#         access_token = 'EAAKFt0cZC5JMBO2IqboZAxN01Qx7XbRUwfTA68E4I8kPg4VZA0tQKCaKNyXXq2q9iiZAeeUbhnNEVhnN7NruzZAvZAHx0ttyqrSRnqpQh9HAHLzGvB29N9zt3U65Xg9HE6vM8GfPCDE8hP3Fwt6Asd0Lj7UFokt3yeQBTARpDR4ZClJWF0ZClzJc4muRoiZAHvrh6PZACabUNBDwr8PKZCt0JnKrvvt'  # Replace with your access token
#         try:
#             graph = facebook.GraphAPI(access_token=access_token, version="3.0")
#         except facebook.GraphAPIError as e:
#             return HttpResponse(f"Error connecting to Facebook Graph API: {e}")

#         leads = []
#         cursor = None

#         while True:
#             try:
#                 params = {'fields': 'field_data,ad_id', 'limit': 100}  # Adjust the limit as needed
#                 if cursor:
#                     params['after'] = cursor
#                 response = graph.get_object(f"/{form_id}/leads", **params)
#                 leads.extend(response['data'])
#                 if 'paging' in response and 'cursors' in response['paging']:
#                     cursor = response['paging']['cursors']['after']
#                 else:
#                     break
#             except facebook.GraphAPIError as e:
#                 return HttpResponse(f"Error retrieving leads: {e}")

# # Create a mapping dictionary for field names
#             field_mapping = {
#                 'nom_de_la_campagne': 'nom_de_la_campagne',
#                 'vous_avez_déjà_travaillé_?': 'avez_vous_travaille',
#                 'full_name': 'nom_prenom',
#                 'phone_number': 'telephone',
#                 'email': 'email',
#             }

# # Process and save the fetched leads to the Lead model
#         for lead_data in leads:
#                 try:
#                     lead = Lead(
#                         nom_de_la_campagne=lead_data.get(field_mapping['nom_de_la_campagne'], ''),
#                         avez_vous_travaille=lead_data.get(field_mapping['vous_avez_déjà_travaillé_?'], ''),
#                         nom_prenom=lead_data.get(field_mapping['full_name'], ''),
#                         telephone=lead_data.get(field_mapping['phone_number'], ''),
#                         email=lead_data.get(field_mapping['email'], ''),
#                         qualification=None,  # Set qualification if available
#                         comments=None,  # Set comments if available
#                         assigned_to=None,  # Set the assigned user if available
#                     )
#                     lead.facebook_page = facebook_page  # Associate the lead with the Facebook page
#                     lead.save()
#                     print(f"Processing after saving Lead Data: {lead_data}")
#                 except Exception as e:
#                     print(f"Error saving lead: {e}")


#         # Fetch all leads after saving the Facebook leads
#         filtered_leads = Lead.objects.all()
#         print('************',filtered_leads)

#         # Render a template to display the leads
#         return render(request, 'lead/leads_dashboard.html', {'fetched_leads': filtered_leads})

#     return HttpResponse("No action taken.")



# views.py
from django.shortcuts import render
from .models import Lead

def filtered_lead_dashboard(request, page_name=None):
    # Get leads associated with the selected Facebook page
    if page_name:
        leads = Lead.objects.filter(facebook_page__page_name=page_name)
    else:
        leads = Lead.objects.all()

    # You can add more logic here to filter and customize the leads display

    return render(request, 'lead/filtered_lead_dashboard.html', {'leads': leads})



from django.shortcuts import render
from django.http import HttpResponse
from . import facebook_script

def fetch_leads(request):
    leads = []  # Initialize an empty list to store the leads
    if request.method == 'POST':
        leads = facebook_script.fetch_leads()  # Call the function from your script to fetch leads

    context = {'leads': leads}
    return render(request, 'lead/fetch_leads.html', context)


@login_required
def facebook_leads(request):
    user = request.user
    is_sales = user.groups.filter(name='sales').exists()
    is_super_admin = user.is_superuser

    # Determine the base template based on user role
    if is_sales:
        base_template = 'sales_base.html'
    elif is_super_admin:
        base_template = 'base.html'
    else:
        base_template = 'sales_base.html'

    context = {
        'base_template': base_template,
    }
    
    return render(request, 'lead/facebook_under.html', context)


import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.shortcuts import render
# from .forms import GoogleSheetForm
from .models import FacebookLead

def gsheet(request):
    if request.method == 'POST':
        form = GoogleSheetForm(request.POST)
        if form.is_valid():
            sheet_link = form.cleaned_data['sheet_link']

            # Set up Google Sheets API credentials
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds_path = os.path.join(os.path.dirname(__file__), 'credentials', 'your_credentials.json')  # Replace 'your_credentials.json' with the actual JSON file name
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            client = gspread.authorize(creds)

            # Open the Google Sheets document based on the provided link
            try:
                sheet = client.open_by_url(sheet_link).sheet1
                data = sheet.get_all_values()

                # Convert the data to a DataFrame using pandas
                df = pd.DataFrame(data[1:], columns=data[0])

                # Optionally, you can process the data as needed before saving it to the database

                # Save the data to the database (assuming YourModel has the same column names as the Google Sheets)
                for index, row in df.iterrows():
                    your_model_instance = FacebookLead(
                        column1=row['Column1'],  # Replace 'Column1', 'Column2', etc. with the actual column names in your Google Sheets
                        column2=row['Column2'],
                        # Add more columns as needed
                    )
                    your_model_instance.save()

                return render(request, 'lead/g-sheet.html', {'form': form, 'success': True})
            except gspread.exceptions.SpreadsheetNotFound:
                return render(request, 'lead/g-sheet.html', {'form': form, 'error': 'Invalid Google Sheets link.'})
    else:
        form = GoogleSheetForm()

    return render(request, 'lead/g-sheet.html', {'form': form})


from django.http import JsonResponse


def get_all_users(request):
    # Fetch all users from the database
    all_users = CustomUserTypes.objects.values('id', 'username')
    return JsonResponse(list(all_users), safe=False)

# In your views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse

def transfer_leads(request):
    
    if request.method == 'POST':
        lead_id = request.POST['leadid']
        username = json.loads(request.POST['username'])  #transfer to
        fulltext = request.POST['fulltext']

        current_user = request.user
      
        username = username.get('username')
        if username:
            new_assigned_transfer = get_object_or_404(CustomUserTypes, username=username)
            if new_assigned_transfer:
                lead = get_object_or_404(Lead, id=lead_id)
                if not lead.current_transfer and lead.transfer_to:
                    lead.current_transfer = lead.transfer_to 

                if lead.current_transfer and lead.transfer_to:
                    lead.current_transfer = lead.transfer_to
                    

                lead.transfer_to = new_assigned_transfer
                lead.is_transferred = True
                lead.save()

                changes = f"{fulltext}"

                # LeadHistory.objects.create(lead=lead, user=current_user, previous_assigned_to=lead.current_assigned_to, current_assigned_to=lead.transfer_to, changes=changes)


                LeadHistory.objects.create(lead=lead, user=current_user,  previous_assigned_to=lead.current_transfer, current_assigned_to=lead.transfer_to, changes=changes, category='mention')

                notification_message = f'You have new mention lead'

                notification = Notification(user=new_assigned_transfer, lead=lead, message=notification_message)
                notification.save()
                return JsonResponse({'success': 'success'}, status=200)
            
        return JsonResponse({'error': 'Username not found'}, status=503)
        
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)



# def parse_date(date_str):
#     try:
#         # Try parsing with format '%Y-%m-%d %H:%M:%S'
#         return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         try:
#             # Try parsing with format '44764,59196'
#             if isinstance(date_str, pd.Timestamp):
#                 date_str = str(date_str)
#             timestamp = float(date_str.replace(',', '.')) * 86400
#             min_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
#             max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

#             # Check if the parsed timestamp is within a reasonable range
#             if min_datetime.timestamp() <= timestamp <= max_datetime.timestamp():
#                 return datetime.fromtimestamp(timestamp)
#             else:
#                 return None
#         except ValueError:
#             return None

# def import_leads(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         try:
#             if file.name.endswith('.csv'):
#                 imported_leads = []
#                 csv_reader = csv.reader(file.read().decode('utf-8').splitlines())
#                 header = next(csv_reader)  # Get the header row
#                 for row in csv_reader:
#                     date_de_soumission = parse_date(row[0].strip('“”'))
#                     if not date_de_soumission:
#                         continue  # Skip this row if date is not valid
#                     lead = Lead(
#                         date_de_soumission=date_de_soumission,
#                         nom_de_la_campagne=row[1],
#                         avez_vous_travaille=row[2],
#                         nom=row[3],
#                         prenom=row[4],
#                         telephone=row[5],
#                         email=row[6],
#                         qualification=row[7],
#                         comments=row[8]
#                     )
#                     imported_leads.append(lead)
#                 Lead.objects.bulk_create(imported_leads)
#             elif file.name.endswith('.xlsx'):
#                 df = pd.read_excel(file)
#                 df = df.where(pd.notna(df), None)  # Convert NaN to None
#                 imported_leads = [
#                     Lead(
#                         date_de_soumission=parse_date(row[0]),
#                         nom_de_la_campagne=row[1],
#                         avez_vous_travaille=row[2],
#                         nom=row[3],
#                         prenom=row[4],
#                         telephone=row[5],
#                         email=row[6],
#                         qualification=row[7],
#                         comments=row[8]
#                     ) for row in df.values
#                 ]
#                 Lead.objects.bulk_create(imported_leads)
#             else:
#                 raise ValueError('Unsupported file format. Please provide a CSV or XLSX file.')

#             messages.success(request, f'{len(imported_leads)} leads imported successfully.')
#         except Exception as e:
#             messages.error(request, f'Error importing leads: {str(e)}')

#     return redirect('lead_dashboard')



# def parse_date(date_str):
#     try:
#         # Try parsing with format '%Y-%m-%d %H:%M:%S'
#         return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         try:
#             # Try parsing with format '44764,59196'
#             timestamp = float(date_str.replace(',', '.')) * 86400
#             min_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
#             max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

#             # Check if the parsed timestamp is within a reasonable range
#             if min_datetime.timestamp() <= timestamp <= max_datetime.timestamp():
#                 return datetime.fromtimestamp(timestamp)
#             else:
#                 return None
#         except ValueError:
#             return None
        




# def parse_date(date_str):
#     try:
#         # Try parsing with format '%Y-%m-%d %H:%M:%S'
#         return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         try:
#             # Try parsing with format '44764,59196'
#             if isinstance(date_str, pd.Timestamp):
#                 date_str = str(date_str)
#             timestamp = float(date_str.replace(',', '.')) * 86400
#             min_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
#             max_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

#             # Check if the parsed timestamp is within a reasonable range
#             if min_datetime.timestamp() <= timestamp <= max_datetime.timestamp():
#                 return datetime.fromtimestamp(timestamp)
#             else:
#                 return None
#         except ValueError:
#             return None


# def delete_lead(request, lead_id):
#     lead = get_object_or_404(Lead, id=lead_id)
#     print('________________-',lead)

#     if request.method == 'POST':
#         # Delete the lead
#         lead.delete()

#         return JsonResponse({'message': 'Lead deleted successfully.'})

#     return JsonResponse({'error': 'Invalid request.'})


# def lead_edit(request, lead_id):
#     lead = get_object_or_404(Lead, id=lead_id)

#     if request.method == 'POST':
#         form_data = request.POST.copy()  # Make a copy of the POST data to modify it
#         assigned_user_id = form_data.get('assigned_to')  # Get the assigned user ID from the form data
#         price = form_data.get('price', None)
#         print("______________________________",price)

#         try:
#             lead.price = Decimal(price) if price else None
#         except (InvalidOperation, TypeError):
#             messages.error(request, 'Invalid price. Please enter a valid number.')
#             return render(request, 'lead/lead_edit.html', {'lead': lead})
        

#         if assigned_user_id:
#             try:
#                 assigned_user = CustomUserTypes.objects.get(id=assigned_user_id)
#                 lead.assigned_to = assigned_user  # Set the assigned user for the lead
#             except CustomUserTypes.DoesNotExist:
#                 # Handle the case when the selected user does not exist (optional)
#                 messages.error(request, 'Invalid user ID selected for assignment.')
                

#         changes = {}

#         # Check if each field has been changed and update the changes dictionary
#         if lead.date_de_soumission != form_data['date_de_soumission']:
#             changes['Date de soumission'] = form_data['date_de_soumission']
# #avez_vous_travaille

#         if lead.avez_vous_travaille != form_data['avez_vous_travaille']:
#             changes['avez_vous_travaille'] = form_data['avez_vous_travaille']

#         if lead.nom_de_la_campagne != form_data['nom_de_la_campagne']:
#             changes['Nom de la campagne'] = form_data['nom_de_la_campagne']
            
#         if lead.nom_prenom != form_data['nom_prenom']:
#             changes['Nom & Prenom'] = form_data['nom_prenom']
            
#         if lead.telephone != form_data['telephone']:
#             changes['Telephone'] = form_data['telephone']
        
#         if lead.email != form_data['email']:
#             changes['Email'] = form_data['email']
        
#         if lead.qualification != form_data['qualification']:
#             changes['Qualification'] = form_data['qualification']
            
#         if lead.comments != form_data['comments']:
#             changes['Comments'] = form_data['comments']

#         # Repeat the above process for other fields

#         # Update the lead instance with the form data
#         lead.date_de_soumission = form_data['date_de_soumission']
#         lead.nom_de_la_campagne = form_data['nom_de_la_campagne']
#         lead.avez_vous_travaille = form_data['avez_vous_travaille']
#         lead.nom_prenom = form_data['nom_prenom']
#         lead.telephone = form_data['telephone']
#         lead.email = form_data['email']
#         lead.comments = form_data['comments']
#         lead.qualification = form_data['qualification']
    

#         # Set the last_modified_by field to the current user
#         lead.last_modified_by = request.user

#         lead.save()
#         #Saving the notification for assign
#         if assigned_user_id:
#             notification_message = f'You have been assigned a new lead: {lead.nom_de_la_campagne}'
#             user = CustomUserTypes.objects.get(id=assigned_user_id)
#             notification = Notification(user=user, lead=lead, message=notification_message)
#             notification.save()
#         messages.success(request, 'Lead edited successfully.')

#         # Create a LogEntry to track the change made by the user
#         content_type = ContentType.objects.get_for_model(Lead)
#         username = request.user.username
#         change_message = f'{username} edited the Lead. Changes: {", ".join([f"{field}: {value}" for field, value in changes.items()])}'
#         log_entry = LogEntry.objects.create(
#             user_id=request.user.id,
#             content_type_id=content_type.id,
#             object_id=lead.id,
#             object_repr=f'{lead}',
#             action_flag=CHANGE,
#             change_message=change_message
#         )

#         context = {
#             'lead': lead,
#             'change_message': change_message,
#             'log_entry': log_entry,
#         }
#         return JsonResponse({'success': True})

#     return render(request, 'lead/lead_edit.html', {'lead': lead})


import facebook
from django.shortcuts import render
from .models import Lead

# def facebook_leads():
#     # Replace 'YOUR_ACCESS_TOKEN' with your actual Facebook access token
#     access_token = 'EAAKFt0cZC5JMBO4bgGrTOyZBZCcVUsZAU9IEzkv1HZBw4es9S7mpH2ezDBM0XcdFENsaHIZCjnYfNCGUCqwXjkIVEZBVYtrUY0ztmriTLCtCCWPD09WBuIVll18igE8Xrd44nvY4wVOGLE7SD5ea1icCEBoDZBcnTZBrueoXZC4CJDiVIpZAaZAMxeg0HM2jyBxJk76TEaQq85fwhIctNpoWfqMikgZDZD'

#     # Create an instance of the Facebook object with your API keys
#     graph = facebook.GraphAPI(access_token=access_token, version="3.0")

#     # Replace 'YOUR_LEADGEN_FORM_ID' with the ID of your lead generation form
#     leadgen_form_id = '314661597574782'

#     # Specify the status parameter as 'all' to get all leads, including expired ones
#     leads = graph.get_object(f"/{leadgen_form_id}/leads", fields='field_data,ad_id')

#     # Process the retrieved leads and save them in your database
#     for lead in leads['data']:
#         date_de_soumission = None
#         nom_de_la_campagne = None
#         avez_vous_travaille = None
#         nom_prenom = None
#         telephone = None
#         email = None
#         qualification = None
#         comments = None

#         for field in lead['field_data']:
#             if field['name'] == 'date_de_soumission':
#                 date_de_soumission = field['values'][0]
#             elif field['name'] == 'nom_de_la_campagne':
#                 nom_de_la_campagne = field['values'][0]
#             elif field['name'] == 'avez_vous_travaille':
#                 avez_vous_travaille = field['values'][0]
#             elif field['name'] == 'nom_prenom':
#                 nom_prenom = field['values'][0]
#             elif field['name'] == 'telephone':
#                 telephone = field['values'][0]
#             elif field['name'] == 'email':
#                 email = field['values'][0]
#             elif field['name'] == 'qualification':
#                 qualification = field['values'][0]
#             elif field['name'] == 'comments':
#                 comments = field['values'][0]

#         if 'ad_id' in lead:
#             status = 'new'
#         else:
#             status = 'expired'

#         # Save the lead to the database
#         Lead.objects.create(
#             date_de_soumission=date_de_soumission,
#             nom_de_la_campagne=nom_de_la_campagne,
#             avez_vous_travaille=avez_vous_travaille,
#             nom_prenom=nom_prenom,
#             telephone=telephone,
#             email=email,
#             qualification=qualification,
#             comments=comments,
#         )

#     print("Leads retrieved and saved successfully.")

# def facebook_leads_view(request):
#     # Call the function to fetch leads from Facebook
#     fetch_facebook_leads()

#     # Retrieve all leads from the database
#     leads = Lead.objects.all()

#     # Pass the leads to the template context
#     context = {
#         'leads': leads
#     }

#     return render(request, 'lead/facebook_leads.html', context)