from django.shortcuts import render, redirect
from accounts.models import CustomUserTypes
from django.contrib.auth.models import User
from .models import Lead
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


def assign_user_to_lead(lead, user_id):
    assigned_user = CustomUserTypes.objects.get(id=user_id)
    lead.assigned_to = assigned_user
    lead.save()
    
    
# def delete_lead(request, lead_id):
#     lead = get_object_or_404(Lead, id=lead_id)
#     print('________________-',lead)

#     if request.method == 'POST':
#         # Delete the lead
#         lead.delete()

#         return JsonResponse({'message': 'Lead deleted successfully.'})

#     return JsonResponse({'error': 'Invalid request.'})


def lead_dashboard(request):
    if request.method == 'POST':
        # Retrieve form data and create a new lead instance
        lead = Lead(
            date_de_soumission=request.POST['date_de_soumission'],
            nom_de_la_campagne=request.POST['nom_de_la_campagne'],
            avez_vous_travaille=request.POST['avez_vous_travaille'],
            nom=request.POST['nom'],
            prenom=request.POST['prenom'],
            telephone=request.POST['telephone'],
            email=request.POST['email'],
            qualification=request.POST['qualification'],
            comments=request.POST['comments']
        )
        lead.save()

        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            assigned_user = CustomUserTypes.objects.get(id=assigned_to_id)
            lead.assigned_to = assigned_user
            lead.save()
        
        return redirect('lead_dashboard')

    # Fetch active leads
    active_leads = Lead.objects.filter(is_active=True)
    users = CustomUserTypes.objects.all()

    return render(request, 'lead/leads_dashboard.html', {'leads': active_leads, 'users': users})


# def lead_list(request):
#     users = CustomUserTypes.objects.all()
#     return render(request, 'lead/leads_dashboard.html', {'users': users})


def lead_edit(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        lead.date_de_soumission = request.POST['date_de_soumission']
        lead.nom_de_la_campagne = request.POST['nom_de_la_campagne']
        lead.avez_vous_travaille = request.POST['avez_vous_travaille']
        lead.nom = request.POST['nom']
        lead.prenom = request.POST['prenom']
        lead.telephone = request.POST['telephone']
        lead.email = request.POST['email']
        lead.qualification = request.POST['qualification']
        lead.comments = request.POST['comments']
        
        # Retrieve the assigned user ID from the request data
        assigned_user_id = request.POST['assigned_to']
        # Get the CustomUserTypes instance corresponding to the user ID
        assigned_user = get_object_or_404(CustomUserTypes, id=assigned_user_id)
        # Assign the user instance to the assigned_to field
        lead.assigned_to = assigned_user
        
        lead.save()
        return JsonResponse({'success': True})

    return render(request, 'lead/lead_edit.html', {'lead': lead})

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


def facebook_leads(request):
    return render(request, 'lead/facebook_leads.html')