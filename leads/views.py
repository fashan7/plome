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



def assign_user_to_lead(lead, user_id):
    assigned_user = CustomUserTypes.objects.get(id=user_id)
    lead.assigned_to = assigned_user
    lead.save()
    

def delete_duplicate_leads():
    # Get all leads
    all_leads = Lead.objects.all()

    # Create a set to store unique lead data (using tuples of fields)
    unique_leads = set()
    duplicates_count = 0

    # Iterate through all leads
    for lead in all_leads:
        # Create a tuple of all lead fields (except id)
        lead_data = (
            lead.date_de_soumission,
            lead.nom_de_la_campagne,
            lead.avez_vous_travaille,
            lead.nom_prenom,
            lead.telephone,
            lead.email,
            lead.qualification,
            lead.comments,
        )

        # Check if the lead_data tuple already exists in the set
        if lead_data in unique_leads:
            # Delete the duplicate lead
            lead.delete()
            duplicates_count += 1
        else:
            # If the tuple does not exist, add it to the set
            unique_leads.add(lead_data)

    return duplicates_count

    

def lead_dashboard(request):
    if request.method == 'POST':
        # Retrieve form data and create a new lead instance
        lead = Lead(
            date_de_soumission=request.POST['date_de_soumission'],
            nom_de_la_campagne=request.POST['nom_de_la_campagne'],
            avez_vous_travaille=request.POST['avez_vous_travaille'],
            nom_prenom=request.POST['nom_prenom'],
            # prenom=request.POST['prenom'],
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
             # Create a notification for the assigned user
            notification_message = f'You have been assigned a new lead: {lead.nom_de_la_campagne}'
            notification = Notification(user=assigned_user, lead=lead, message=notification_message)
            notification.save()

            # Store the notification message in the session for the current user
            request.session['assigned_message'] = notification_message
            print("Assigned Message:", request.session['assigned_message'])
            
            
        duplicates_deleted = delete_duplicate_leads()
        messages.success(request, f'{lead.nom_de_la_campagne} leads added successfully. {duplicates_deleted} duplicate leads deleted.')
        return redirect('lead_dashboard')

    # Fetch active leads
    active_leads = Lead.objects.filter(is_active=True).order_by('-date_de_soumission')
    users = CustomUserTypes.objects.all()
    ##fashan------------------------------------
    nav_data = navigation_data(request.user.id)


    return render(request, 'lead/leads_dashboard.html', {'leads': active_leads, 'users': users,'sections': nav_data})


# def lead_list(request):
#     users = CustomUserTypes.objects.all()
#     return render(request, 'lead/leads_dashboard.html', {'users': users})

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

        # Update the lead instance with the form data
        # lead.date_de_soumission = form_data['date_de_soumission']
        # lead.nom_de_la_campagne = form_data['nom_de_la_campagne']
        # lead.avez_vous_travaille = form_data['avez_vous_travaille']
        # lead.nom_prenom = form_data['nom_prenom']
        # lead.telephone = form_data['telephone']
        # lead.email = form_data['email']
        # lead.qualification = form_data['qualification']
        # lead.comments = form_data['comments']
        # lead.last_modified_by = request.user

        # Save the lead instance to the database

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
        LogEntry.objects.create(
            user_id=request.user.id,
            #user_name = request.user.assigned_to,
            content_type_id=content_type.id,
            object_id=lead.id,
            object_repr=f'{lead}',
            action_flag=CHANGE,
            change_message=change_message
        )
        # print("************************",LogEntry.change_message)

        context = {
            'lead': lead,
            'change_message': change_message
        }
        print("****************************",context)


        return JsonResponse({'success': True})

    return render(request, 'lead/lead_edit.html', {'lead': lead})


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





        


import pandas as pd


def parse_date(date_string):
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

def import_leads(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            if file.name.endswith('.csv'):
                imported_leads = []
                csv_reader = csv.reader(file.read().decode('utf-8').splitlines())
                header = next(csv_reader)  # Get the header row
                for row in csv_reader:
                    date_de_soumission = parse_date(row[0].strip('“”'))
                    
                    if not date_de_soumission:
                        continue  # Skip this row if date is not valid
                        
                    telephone = int(float(row[4])) if row[4].strip() else None
                    lead = Lead(
                        date_de_soumission=date_de_soumission,
                        nom_de_la_campagne=row[1] or '',
                        avez_vous_travaille=row[2] or '',
                        nom_prenom=row[3] or '',
                        telephone=telephone,
                        email=row[5] or '',
                        qualification=row[6] or '',
                        comments=row[7] or ''
                    )
                    imported_leads.append(lead)
                Lead.objects.bulk_create(imported_leads)
            elif file.name.endswith('.xlsx'):
                
                # Convert XLSX to CSV
                df = pd.read_excel(file)
                csv_tempfile = 'tempfile.csv'
                df.to_csv(csv_tempfile, index=False, encoding='utf-8', na_rep='')  # Set na_rep to an empty string

                # Read the CSV and process it
                with open(csv_tempfile, 'r', encoding='utf-8') as csv_file:
                    imported_leads = []
                    csv_reader = csv.reader(csv_file)
                    header = next(csv_reader)  # Get the header row
                    for row in csv_reader:
                        date_de_soumission = parse_date(row[0].strip('“”'))
                        if not date_de_soumission:
                            continue  # Skip this row if date is not valid
                        lead = Lead(
                            date_de_soumission=date_de_soumission,
                            nom_de_la_campagne=row[1] or '',
                            avez_vous_travaille=row[2] or '',
                            nom_prenom=row[3] or '',
                            telephone=row[4] or '',
                            email=row[5] or '',
                            qualification=row[6] or '',
                            comments=row[7] or ''
                        )
                        imported_leads.append(lead)
                    Lead.objects.bulk_create(imported_leads)

            else:
                raise ValueError('Unsupported file format. Please provide a CSV or XLSX file.')
# Delete duplicate leads
            duplicates_deleted = delete_duplicate_leads()

            messages.success(request, f'{len(imported_leads)} leads imported successfully. {duplicates_deleted} duplicate leads deleted.')
        except Exception as e:
            messages.error(request, f'Error importing leads: {str(e)}')

    return redirect('lead_dashboard')




def delete_leads(request):
    if request.method == 'POST' and request.is_ajax():
        lead_ids = request.POST.getlist('lead_ids[]')
        Lead.objects.filter(id__in=lead_ids).delete()
        return JsonResponse({'success': True, 'message': 'Selected leads deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})



def facebook_leads(request):
    file_path = r'E:\games 2\plome-main\fake_api.py'
    if not os.path.exists(file_path):
        return render(request, 'lead/facebook_leads.html', {'error': 'File not found.'})

    spec = importlib.util.spec_from_file_location('leads_data', file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    leads_data = module.leads_data

    leads_added_by_api = []
    for data in leads_data:
        try:
            lead = Lead.objects.create(
                date_de_soumission=data['Date de Soumission'],
                nom_de_la_campagne=data['Nom de la Campagne'],
                avez_vous_travaille=data['Avez-vous travaillé'],
                nom_prenom=data['Nom & Prenom'],
                # prenom=data['Prénom'],
                telephone=data['Téléphone'],
                email=data['Email'],
                qualification=data['Qualification'],
                comments=data['Comments'],
                added_by_api=True,
            )
            leads_added_by_api.append(lead)
        except Exception as e:
            # Handle any errors that occur during lead creation
            print(f"Error creating lead: {e}")

    return render(request, 'lead/facebook_leads.html', {'leads': leads_added_by_api})


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
    user_leads = Lead.objects.filter(assigned_to=request.user, is_active=True)
    return render(request, 'lead/sales_lead.html', {'leads': user_leads})

    # users = CustomUserTypes.objects.all()
    # nav_data = navigation_data(request.user.id)
    # return render(request, 'lead/sales_lead.html', {'leads': user_leads})




# def facebook_leads(request):
#     return render(request, 'lead/facebook_leads.html')


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
