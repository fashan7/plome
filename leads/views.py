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
from .models import Lead



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
@user_passes_test(is_superuser, login_url='dashboard_sales')
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


# @login_required
# def user_dashboard(request):
#     user = request.user
#     assigned_leads_count = Lead.objects.filter(assigned_to=user).count()
    
#     context = {
#         'assigned_leads_count': assigned_leads_count
#     }
#     return render(request, 'lead/dashboard-sales.html', context)



#deleting the duplicates only if there numbers are same
def delete_duplicate_leads():
    # Get all leads ordered by id (to keep the latest lead for each unique telephone number)
    all_leads = Lead.objects.order_by('id')

    # Create a set to store unique telephone numbers
    unique_telephones = set()

    duplicates_count = 0

    # Iterate through all leads
    for lead in all_leads:
        # Check if the telephone number is already in the set
        if lead.telephone in unique_telephones:
            # Delete the duplicate lead
            lead.delete()
            duplicates_count += 1
        else:
            # If the telephone number is not in the set, add it to the set
            unique_telephones.add(lead.telephone)

    return duplicates_count



from .models import Notification

from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Lead, CustomUserTypes

def filtered_lead_dashboard(request, user_id):
    # Fetch active leads for the selected user
    active_leads = Lead.objects.filter(is_active=True, assigned_to__id=user_id).order_by('-date_de_soumission')
    users = CustomUserTypes.objects.all()
    nav_data = navigation_data(request.user.id)

    return render(request, 'lead/leads_dashboard.html', {'leads': active_leads, 'users': users, 'sections': nav_data})



from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Lead, CustomUserTypes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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
            
            return HttpResponseRedirect(f'/filtered_lead_dashboard/{assigned_user.id}/?notification={notification_message}')
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

        return render(request, 'lead/leads_dashboard.html', {'leads': filtered_leads, 'users': users, 'sections': nav_data})



#this function is used for history of mention 
from .models import *

def lead_history_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead_history = LeadHistory.objects.filter(lead=lead).order_by('-timestamp')
    return render(request, 'lead/lead_history.html', {'lead': lead, 'history_entries': lead_history})


def lead_list(request):
    leads = Lead.objects.all()
    return render(request, 'lead/lead_list.html', {'leads': leads})

def lead_history(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    history_entries = LeadHistory.objects.filter(lead=lead)
    return render(request, 'lead/lead_history.html', {'lead': lead, 'history_entries': history_entries})

def save_appointment(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')

        lead = Lead.objects.get(pk=lead_id)
        lead.appointment_date_time = datetime.combine(
            datetime.strptime(appointment_date, '%Y-%m-%d').date(),
            datetime.strptime(appointment_time, '%H:%M').time()
        )
        lead.save()
        '''
        send_mail(
            'Appointment Scheduled',
            f'Your appointment is scheduled on {lead.appointment_date_time}.',
            'sender@example.com',
            [lead.email],
            fail_silently=False,
        )
        '''
        return JsonResponse({'success': True})
        
    return JsonResponse({'success': False})

def save_signe_cpf(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        price = request.POST.get('price')

        try:
            lead = Lead.objects.get(id=lead_id)
            lead.price = price
            lead.save()
            return JsonResponse({'success': True})
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

    return render(request, 'lead_dashboard.html', {'lead': lead})


from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Attachment
from urllib.parse import unquote 

def download_attachment(request, attachment_id, attachment_name):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    
    response = FileResponse(attachment.file, as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{unquote(attachment_name)}"'
    
    return response

from django.http import JsonResponse\
    
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
        if lead.date_de_soumission != form_data['date_de_soumission']:
            changes['Date de soumission'] = form_data['date_de_soumission']
#avez_vous_travaille

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

        custom_fields_data = {}
        for key, value in form_data.items():
            if key.startswith('custom_fields.'):
                custom_field_key = key.split('.', 1)[1]
                custom_fields_data[custom_field_key] = value
        lead.custom_fields = custom_fields_data

    

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

        context = {
            'lead': lead,
            'change_message': change_message,
            'log_entry': log_entry,
        }
        return JsonResponse({'success': True})

    return render(request, 'lead/lead_edit.html', {'lead': lead})


#can be used in future 

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

            return JsonResponse({'success': True, 'message': 'Leads assigned successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)


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

def toggle_saleslead_status(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.is_complete = not lead.is_complete  # Toggle the status
    lead.save()

    if lead.is_complete:
        return redirect('complete_leads')
    else:
        return redirect('sales_lead')

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
                # print(headers)
                

                additional_headers = [header for header in headers if header not in field_map]
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
                    if header == 'custom_fields':
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



@login_required
def sales_lead(request):    
    user_leads = Lead.objects.filter(assigned_to=request.user, is_active=True, is_complete=False )
    return render(request, 'lead/sales_lead.html', {'leads': user_leads})


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

            return JsonResponse({'success': True, 'message': 'Leads assigned successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)


    # users = CustomUserTypes.objects.all()
    # nav_data = navigation_data(request.user.id)
    # return render(request, 'lead/sales_lead.html', {'leads': user_leads})


# views.py


# from django.shortcuts import render, HttpResponse
# import json
# import facebook
# from .models import Lead, FacebookLead, CustomUserTypes

# def fetch_facebook_leads(request):
#     print("Fetching Facebook leads...")
#     # Retrieve all users from the database
#     users = CustomUserTypes.objects.all()

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')

#         # Check if a user with the provided user_id exists
#         try:
#             selected_user = CustomUserTypes.objects.get(pk=user_id)
#         except CustomUserTypes.DoesNotExist:
#             return HttpResponse(json.dumps({'error': 'Selected user does not exist.'}), content_type='application/json')

#         # Get the Facebook lead generation form ID associated with the selected user
#         if selected_user.Username == 'Jatin':
#             leadgen_form_id = '314661597574782'
#         # elif selected_user.username == 'fashan':
#         #     leadgen_form_id = 'YOUR_LEADGEN_FORM_ID_FOR_FASHAN'
#         else:
#             # Handle the case where the user is not selected or not found
#             return HttpResponse(json.dumps({'error': 'Invalid selected user.'}), content_type='application/json')

#         # Replace 'YOUR_ACCESS_TOKEN' with your actual Facebook access token
#         access_token = 'EAAKFt0cZC5JMBO6FUZB1kXfNLkw0xcZAjm1fAsK1rZBtEKf67H6wwFA40pC7SZBKf5zrrmyEcD0OoyOunHK824hyQ0pse0rEVsbMYesOXAL5Cw0ZBmPo5gQx6AfMALSzwJ9Id0dFnJ28SDj258fz8uxFIJLddiipOxh6fjJdr9cURhQJvnLkpCwQoFEv6KwKfxaBkjwEWKmJ11f2aigzrT'

#         # Create an instance of the Facebook object with your API keys
#         graph = facebook.GraphAPI(access_token=access_token, version="3.0")

#         # Specify the status parameter as 'all' to get all leads, including expired ones
#         leads = graph.get_object(f"/{leadgen_form_id}/leads", fields='field_data,ad_id')

#         # Process the retrieved leads and create a list of leads
#         leads_list = []
#         for lead in leads['data']:
#             lead_data = {
#                 'user': selected_user,
#                 'ad_id': lead.get('ad_id'),
#             }

#             for field in lead['field_data']:
#                 field_name = field['name']
#                 field_value = field['values'][0]
#                 lead_data[field_name] = field_value

#             leads_list.append(lead_data)

#         # Save the leads to the database
#         FacebookLead.objects.bulk_create([FacebookLead(**data) for data in leads_list])

#         # You can also do additional processing or filtering of leads based on the user if needed
#         # leads_list = [lead for lead in leads_list if lead['user'] == selected_user]

#         return HttpResponse(json.dumps(leads_list), content_type='application/json')

#     # If it's a GET request, render the template with the list of users
#     context = {
#         'users': users,
#     }
#     return render(request, 'lead/facebook.html', context)





from django.shortcuts import render, HttpResponse
import json
import facebook

def fetch_facebook_leads(request):
    if request.method == 'POST':
        user = request.POST.get('user')

        # Replace 'YOUR_ACCESS_TOKEN' with your actual Facebook access token
        access_token = 'EAAKFt0cZC5JMBO6FUZB1kXfNLkw0xcZAjm1fAsK1rZBtEKf67H6wwFA40pC7SZBKf5zrrmyEcD0OoyOunHK824hyQ0pse0rEVsbMYesOXAL5Cw0ZBmPo5gQx6AfMALSzwJ9Id0dFnJ28SDj258fz8uxFIJLddiipOxh6fjJdr9cURhQJvnLkpCwQoFEv6KwKfxaBkjwEWKmJ11f2aigzrT'

        # Create an instance of the Facebook object with your API keys
        try:
            graph = facebook.GraphAPI(access_token=access_token, version="3.0")
        except facebook.GraphAPIError as e:
            print(f"Error connecting to Facebook Graph API: {e}")
            return

        # Replace 'YOUR_LEADGEN_FORM_ID' with the ID of your lead generation form
        leadgen_form_id = '314661597574782'
        # Specify the status parameter as 'all' to get all leads, including expired ones
        try:
            leads = graph.get_object(f"/{leadgen_form_id}/leads", fields='field_data,ad_id')
        except facebook.GraphAPIError as e:
            print(f"Error retrieving leads: {e}")
            return

        # Process the retrieved leads and create a list of leads
        leads_list = []
        for lead in leads['data']:
            campaign_name = None
            avez_vous_travaille = None
            form_name = None
            name = None
            email = None
            phone = None
            created_time = None

            for field in lead['field_data']:
                if field['name'] == 'full_name':
                    name = field['values'][0]
                elif field['name'] == 'email':
                    email = field['values'][0]
                elif field['name'] == 'phone_number':
                    phone = field['values'][0]
                elif field['name'] == 'nom_de_la_campagne':
                    campaign_name = field['values'][0]
                elif field['name'] == 'avez_vous_travaille':
                    avez_vous_travaille = field['values'][0]
                elif field['name'] == 'form_name':
                    form_name = field['values'][0]
                

            if 'ad_id' in lead:
                status = 'new'
            else:
                status = 'expired'

            leads_list.append({
                'campaign_name': campaign_name,
                'vous_avez_travaille': avez_vous_travaille,
                'name': name,
                'email': email,
                'phone': phone,
                'form_name' : form_name,
                'status': status,
            })

        # Pass the leads list to the template
        context = {
            'leads': leads_list
        }
        return render(request, 'lead/facebook.html', context)

    return render(request, 'lead/facebook.html')




def facebook_leads(request):
    pass

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


                LeadHistory.objects.create(lead=lead, user=current_user,  previous_assigned_to=lead.current_transfer, current_assigned_to=lead.transfer_to, changes=changes)

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