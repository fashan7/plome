from django.db import models
from django.forms import JSONField
from accounts.models import User
from accounts.models import CustomUserTypes
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver



class LeadHistory(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='lead_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    previous_assigned_to = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_assigned_leads')
    current_assigned_to = models.ForeignKey(CustomUserTypes, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_assigned_leads')
    changes = models.TextField()
    CATEGORY_CHOICES = (
        ('assign', 'Assign'),
        ('mention', 'Mention'),
        ('other', 'Other'),
    )
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')

    class Meta:
        ordering = ['-timestamp']

class FacebookPage(models.Model):
    form_id = models.CharField(max_length=100)
    page_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    

    def __str__(self):
        return self.page_name

class token(models.Model):
    access_token = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.access_token

class Lead(models.Model):
    date_de_soumission = models.DateField(null=True, blank=True)
    nom_de_la_campagne = models.CharField(max_length=100, null=True, blank=True)
    avez_vous_travaille = models.CharField(max_length=100, null=True, blank=True)
    nom_prenom = models.CharField(max_length=100, null=True, blank=True)
    # prenom = models.CharField(max_length=100)
    #telephone = models.CharField(max_length=20, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
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
    appointment_date_time = models.DateTimeField(null=True, blank=True)
    reminder_timestamp = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    read_mail = models.BooleanField(default=False)
    LEAD_SOURCE_CHOICES = (
        ('facebook', 'Facebook'),
        ('imported', 'Imported'),
    )

    lead_source = models.CharField(max_length=100, choices=LEAD_SOURCE_CHOICES, default='imported')
    facebook_page = models.ForeignKey(FacebookPage, on_delete=models.SET_NULL, null=True, blank=True)
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
         return str(self.nom_prenom)
    

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

@receiver(post_save, sender=Lead)
def create_lead_history(sender, instance, created, **kwargs):
    if created:
        LeadHistory.objects.create(lead=instance, user=instance.last_modified_by, previous_assigned_to=instance.current_transfer, current_assigned_to=instance.transfer_to, changes="Lead created.")
    else:
        changes = []
        for field, value in instance._original_state.items():
            new_value = getattr(instance, field)

            

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
    is_hidden = models.BooleanField(default=False)

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
    
    
from django.db import models
from .models import Lead  # Import the original Lead model

    
    
class Attachment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='lead_attachments/')
    title = models.CharField(max_length=100)  # Additional field for attachment title

    # Additional fields for attachment metadata (e.g., description, etc.)

    def __str__(self):
        return f"Attachment for Lead: {self.lead.nom_de_la_campagne}"
    

class PriceEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.entry_date} - ${self.price}"
    




from django.db import models
from django.contrib.auth.models import User


class FetchedLead(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    facebook_lead_id = models.CharField(max_length=255, unique=True)





