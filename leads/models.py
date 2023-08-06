from django.db import models
from django.forms import JSONField
from accounts.models import User
from accounts.models import CustomUserTypes
from django.dispatch import receiver
from django.db.models.signals import post_save


class LeadHistory(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='lead_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    previous_assigned_to = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_assigned_leads')
    current_assigned_to = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_assigned_leads')
    changes = models.TextField()

    class Meta:
        ordering = ['-timestamp']

class Lead(models.Model):
    date_de_soumission = models.DateField(null=True, blank=True)
    nom_de_la_campagne = models.CharField(max_length=100, null=True, blank=True)
    avez_vous_travaille = models.CharField(max_length=100, null=True, blank=True)
    nom_prenom = models.CharField(max_length=100, null=True, blank=True)
    # prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    QUALIFICATION_CHOICES = (
        ('nrp1', 'NRP1'),
        ('nrp2', 'NRP2'),
        ('nrp3', 'NRP3'),
        ('en_cours', 'En cours'),
        ('rappel', 'Rappel'),
        ('faux_numero', 'Faux numéro'),
        ('pas_de_budget', 'Pas de budget'),
        ('pas_interesse', 'Pas intéressé'),
        ('ne_pas_rappele', 'Ne pas rappeler'),
        ('signe_pole_emploi', 'Signé Pôle Emploi'),
        ('signe_cpf', 'Signé CPF'),
    )
    qualification = models.CharField(max_length=100, choices=QUALIFICATION_CHOICES, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    custom_fields = models.JSONField(null=True, blank=True)
    current_transfer = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_transferred_leads')
    transfer_to = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferred_leads')
    is_transferred = models.BooleanField(default=False)

    assign_comment = models.JSONField(null=True, blank=True)
    history = models.ForeignKey(LeadHistory, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    _original_state = {}
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the original state of the instance
        self._original_state = self.__dict__.copy()
     
    def __str__(self):
        return str(self.nom_de_la_campagne)

    
        
    def add_user_mention(self, user_id, username):
        # Add a new user mention to the assign_comment field
        mention = {"user_id": user_id, "username": username}
        self.assign_comment.append(mention)

    def remove_user_mention(self, user_id):
        # Remove a user mention from the assign_comment field
        self.assign_comment = [mention for mention in self.assign_comment if mention.get("user_id") != user_id]

    def get_user_mentions(self):
        # Return the list of user mentions in the assign_comment field
        return self.assign_comment
        
    def __str__(self):
         return str(self.nom_de_la_campagne)
    
    
# @receiver(post_save, sender=Lead)
# def track_lead_changes(sender, instance, created, **kwargs):
#     if created:
#         changes = "Lead created."
#     else:
#         changes = ""
#         for field, value in instance._original_state.items():
#             if getattr(instance, field) != value:
#                 changes += f"{field}: {value} -> {getattr(instance, field)}\n"

#     # Create a LeadHistory entry if there are any changes
#     if changes:
#         LeadHistory.objects.create(lead=instance, user=instance.last_modified_by, assigned_to=instance.assigned_to, changes=changes)
    
# Register the signal receiver to create LeadHistory entries
from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=Lead)
def create_lead_history(sender, instance, created, **kwargs):
    if created:
        LeadHistory.objects.create(lead=instance, user=instance.last_modified_by, previous_assigned_to=instance.current_transfer, current_assigned_to=instance.transfer_to, changes="Lead created.")
    else:
        changes = []
        for field, value in instance._original_state.items():
            new_value = getattr(instance, field)
            if new_value != value:
                # Customize the message for specific fields
                if field == 'qualification':
                    old_qualification = dict(instance.QUALIFICATION_CHOICES).get(value, value)
                    new_qualification = dict(instance.QUALIFICATION_CHOICES).get(new_value, new_value)
                    changes.append(f"- {instance.last_modified_by.username} ---- changed qualification from ---- '{old_qualification}' --to '{new_qualification}'.")
                elif field == 'assigned_to':
                    old_assigned_to_name = CustomUserTypes.objects.get(id=value).get_username() if value else "Unassigned"
                    new_assigned_to_name = CustomUserTypes.objects.get(id=new_value).get_username() if new_value else "Unassigned"
                    changes.append(f"- {instance.last_modified_by.username} changed assigned user from '{old_assigned_to_name}' to '{new_assigned_to_name}'.")
                    LeadHistory.objects.create(lead=instance, user=instance.last_modified_by, previous_assigned_to=value, current_assigned_to=new_value, changes="Lead transferred.")
                else:
                    changes.append(f"- {field}: {value} -> {new_value}")
        # Check if any changes were made
        if changes:
            # Join all the messages into a single string
            changes_str = "\n".join(changes)
            LeadHistory.objects.create(lead=instance, user=instance.last_modified_by, previous_assigned_to=instance.current_transfer, current_assigned_to=instance.transfer_to, changes=changes_str)
      
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return self.message
    
# models.py

class FacebookLead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_de_soumission = models.DateField()
    nom_de_la_campagne = models.CharField(max_length=100)
    avez_vous_travaille = models.CharField(max_length=100)
    nom_prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    qualification = models.CharField(max_length=100)
    comments = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user
    
    

    
