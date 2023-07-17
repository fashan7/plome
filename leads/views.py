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
    
    
def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        # Delete the lead
        lead.delete()

        return JsonResponse({'message': 'Lead deleted successfully.'})

    return JsonResponse({'error': 'Invalid request.'})


def lead_dashboard(request):
    if request.method == 'POST':
        # Retrieve form data
        date_de_soumission = request.POST['date_de_soumission']
        nom_de_la_campagne = request.POST['nom_de_la_campagne']
        avez_vous_travaille = request.POST['avez_vous_travaille']
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        telephone = request.POST['telephone']
        email = request.POST['email']
        qualification = request.POST['qualification']
        comments = request.POST['comments']

        # Create a new lead instance
        lead = Lead(
            date_de_soumission=date_de_soumission,
            nom_de_la_campagne=nom_de_la_campagne,
            avez_vous_travaille=avez_vous_travaille,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            qualification=qualification,
            comments=comments
        )
        lead.save()
        
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            assigned_user = CustomUserTypes.objects.get(id=assigned_to_id)
            lead.assigned_to = assigned_user
            lead.save()
        return redirect('lead_dashboard')
            

    # Fetch all leads
    leads = Lead.objects.all()
    users = CustomUserTypes.objects.all()


    return render(request, 'lead/leads_dashboard.html', {'leads': leads,'users': users})


# def lead_list(request):
#     users = CustomUserTypes.objects.all()
#     return render(request, 'lead/leads_dashboard.html', {'users': users})


def lead_edit(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    
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
        
        lead.save()
        
        return redirect('leads_dashboard')
    
    return render(request, 'lead/lead_edit.html', {'lead': lead})






# def lead_delete(request, lead_id):
#     lead = Lead.objects.get(id=lead_id)
#     lead.delete()
#     return redirect('lead_add')




