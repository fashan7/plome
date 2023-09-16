# # multi_company/views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from accounts.models import CustomUserTypes
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import User

from django.shortcuts import render
from .models import Company  # Import the Company model
def company_dropdown_view(request):
    companies = Company.objects.all()
    return {'companies': companies}

    

def doisser(request):
    return render(request,'multi_company/doisser.html')


import csv
import math
import pandas as pd
from datetime import datetime, timezone
from django.contrib import messages

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

# multi_company/views.py
import json
import math
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Doisser

def parse_date(date_string):
    try:
        return pd.to_datetime(date_string, errors='coerce')
    except Exception as e:
        return None


def doisser(request):
    records = Doisser.objects.all()  # Fetch all Doisser records from the database
    return render(request, 'multi_company/doisser.html', {'records': records})

def import_doisser_leads(request):
    field_map = {
        'date_dinscription': 'Date d\'inscription',
        'numero_edof': 'Numéro EDOF',
        'nom': 'Nom',
        'prenom': 'Prénom',
        'telephone': 'Numéro de téléphone',
        'mail': 'Mail',
        'address_postal': 'Adresse Postale',
        'statut_edof': 'Statut EDOF',
        'challenge': 'Chalenge',
        'colis_a_preparer': 'Colis à Préparer',
        'prix_net': 'Prix Net',
        'conseiller': 'Conseiller',
        'equipes': 'Équipes',
        'criteres_com': 'Critères com',
        'date_prevue_d_entree_en_formation': 'Date Prévue d\'entrée en Formation',
        'date_prevue_de_fin_de_formation': 'Date Prévue de Fin de Formation',
        
        # Fields from AppelEffectueLe model
        'appel_effectue_le_date_time': 'Date/Heure de l\'appel effectué',
        'appel_effectue_le_motifs': 'Motifs de l\'appel effectué',
        
        # Fields from RdvConfirme model
        'rdv_confirme_dateandtime': 'Date/Heure du RDV confirmé',
        'rdv_confirme_confirmateur': 'Confirmateur du RDV',
        'rdv_confirme_statut_service_confirmateur': 'Statut du service du confirmateur du RDV',
        
        # Fields from InscriptionVisioEntree model
        'inscription_visio_entree_audio': 'Audio lors de l\'inscription à la visio',
        'inscription_visio_entree_niveau_de_relance': 'Niveau de relance lors de l\'inscription à la visio',
        'inscription_visio_entree_somme_facturee': 'Somme facturée lors de l\'inscription à la visio',
        'inscription_visio_entree_date_de_facturation': 'Date de facturation lors de l\'inscription à la visio',
        'inscription_visio_entree_date_d_encaissement': 'Date d\'encaissement lors de l\'inscription à la visio',
        'inscription_visio_entree_facture': 'Facture lors de l\'inscription à la visio',
        'inscription_visio_entree_num_facture': 'Numéro de facture lors de l\'inscription à la visio',
        'inscription_visio_entree_colis_a_envoyer_le': 'Date de colis à envoyer lors de l\'inscription à la visio',
        'inscription_visio_entree_numero_de_suivi_vers_point_relais': 'Numéro de suivi vers le point relais lors de l\'inscription à la visio',
        'inscription_visio_entree_commentaires': 'Commentaires lors de l\'inscription à la visio',
        'inscription_visio_entree_statut_colis': 'Statut du colis lors de l\'inscription à la visio',
    }

    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            try:
                if file.name.endswith('.xls') or file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    raise ValueError("Unsupported file format. Only XLS and XLSX files are allowed.")

                headers = [header.strip() for header in df.columns]
                field_map_normalized = {key.lower().replace(" ", "_"): value for key, value in field_map.items()}
                filtered_headers = [header for header in headers if header.lower() in field_map_normalized.values()]

                additional_headers = [header for header in headers if header.lower() not in field_map_normalized.values()]
                filtered_headers_lower = [header.lower() for header in filtered_headers]
                filtered_field_map = {key: value for key, value in field_map.items() if value in filtered_headers_lower}

                df_dict = df.to_dict(orient='records')
                json_data = json.dumps(df_dict, default=date_handler)
                request.session['df'] = json_data
                request.session['field_map'] = field_map

                context = {'headers': headers, 'field_map': field_map, 'additional_headers': additional_headers}
                return render(request, 'multi_company/mapping_dossier_modal.html', context)
            except Exception as e:
                messages.error(request, f'Error reading file: {str(e)}')
                return redirect('doisser')

        elif 'mapping' in request.POST:
            mapping_data = {}
            custom_fields = {}

            for field, field_name in field_map.items():
                mapping_data[field] = request.POST.get(field, '')

            for custom_field in request.POST.getlist('custom_fields'):
                custom_fields[custom_field] = custom_field

            mapping_data.update({'custom_fields': custom_fields})

            df_records = request.session.get('df', [])
            field_map = request.session.get('field_map', {})

            leads = []
            for record in json.loads(df_records):
                lead_data = {}
                for header, field in mapping_data.items():
                    if field == '__empty__':
                        value_holder = None
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
                        if header.startswith('date_'):
                            date_value = parse_date(value)
                            value_holder = date_value if not pd.isna(date_value) else None
                        elif isinstance(value, float) and math.isnan(value):
                            value_holder = ''
                        elif isinstance(value, float) and not math.isnan(value):
                            value_holder = int(value) if value.is_integer() else value
                        else:
                            value_holder = record[field]

                        lead_data[header] = value_holder

                leads.append(Doisser(**lead_data))

            Doisser.objects.bulk_create(leads)
            request.session.pop('df', None)
            request.session.pop('field_map', None)

            messages.success(request, f'{len(leads)} leads imported successfully.')

            return redirect('doisser')

    return redirect('doisser')





# def import_doisser_leads(request):
#     field_map = {
#         'date_dinscription': 'Date d\'inscription',
#         'numero_edof': 'Numéro EDOF',
#         'nom': 'Nom',
#         'prenom': 'Prénom',
#         'telephone': 'Numéro de téléphone',
#         'mail': 'Mail',
#         'address_postal': 'Adresse Postale',
#         'statut_edof': 'Statut EDOF',
#         'challenge': 'Chalenge',
#         'colis_a_preparer': 'Colis à Préparer',
#         'prix_net': 'Prix Net',
#         'conseiller': 'Conseiller',
#         'equipes': 'Équipes',
#         'criteres_com': 'Critères com',
#         'date_prevue_d_entree_en_formation': 'Date Prévue d\'entrée en Formation',
#         'date_prevue_de_fin_de_formation': 'Date Prévue de Fin de Formation',
#     }
    
#     if request.method == 'POST':
#         if 'file' in request.FILES:
#             file = request.FILES['file']
#             try:
#                 if file.name.endswith('.xls') or file.name.endswith('.xlsx'):
#                     df = pd.read_excel(file)
#                 else:
#                     raise ValueError("Unsupported file format. Only XLS and XLSX files are allowed.")

#                 headers = [header.strip() for header in df.columns]
#                 field_map_normalized = {key.lower().replace(" ", "_"): value for key, value in field_map.items()}
#                 filtered_headers = [header for header in headers if header.lower() in field_map_normalized.values()]

#                 additional_headers = [header for header in headers if header.lower() not in field_map_normalized.values()]
#                 filtered_headers_lower = [header.lower() for header in filtered_headers]
#                 filtered_field_map = {key: value for key, value in field_map.items() if value in filtered_headers_lower}

#                 df_dict = df.to_dict(orient='records')
#                 json_data = json.dumps(df_dict, default=date_handler)
#                 request.session['df'] = json_data
#                 request.session['field_map'] = field_map

#                 context = {'headers': headers, 'field_map': field_map, 'additional_headers': additional_headers}
#                 return render(request, 'multi_company/mapping_dossier_modal.html', context)
#             except Exception as e:
#                 messages.error(request, f'Error reading file: {str(e)}')
#                 return redirect('doisser')

#         elif 'mapping' in request.POST:
#             mapping_data = {}
#             custom_fields = {}

#             for field, field_name in field_map.items():
#                 mapping_data[field] = request.POST.get(field, '')

#             for custom_field in request.POST.getlist('custom_fields'):
#                 custom_fields[custom_field] = custom_field

#             mapping_data.update({'custom_fields': custom_fields})

#             df_records = request.session.get('df', [])
#             field_map = request.session.get('field_map', {})

#             leads = []
#             for record in json.loads(df_records):
#                 lead_data = {}
#                 for header, field in mapping_data.items():
#                     if field == '__empty__':
#                         value_holder = None
#                     elif header == 'custom_fields':
#                         custom_f = {}
#                         for excess_key, excess_fields in field.items():
#                             excess_value = record.get(excess_key)
#                             excess_value_holder = None
#                             if (isinstance(excess_value, float) and math.isnan(excess_value)) or excess_value == 'NaT':
#                                 excess_value_holder = ''
#                             else:
#                                 excess_value_holder =  excess_value
#                             custom_f[excess_key] = excess_value_holder
#                         lead_data['custom_fields'] = custom_f
#                     else:
#                         value = record.get(field)
#                         value_holder = None
#                         if header.startswith('date_'):
#                             date_value = parse_date(value)
#                             value_holder = date_value if not pd.isna(date_value) else None
#                         elif isinstance(value, float) and math.isnan(value):
#                             value_holder = ''
#                         elif isinstance(value, float) and not math.isnan(value):
#                             value_holder = int(value) if value.is_integer() else value
#                         else:
#                             value_holder = record[field]

#                         lead_data[header] = value_holder

#                 leads.append(Doisser(**lead_data))

#             Doisser.objects.bulk_create(leads)
#             request.session.pop('df', None)
#             request.session.pop('field_map', None)

#             messages.success(request, f'{len(leads)} leads imported successfully.')

#             return redirect('doisser')

#     return redirect('doisser')





