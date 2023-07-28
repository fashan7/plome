from django.db import models
from accounts.models import User

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
    
    is_active = models.BooleanField(default=True)
    custom_fields = models.JSONField(null=True, blank=True)



    def __str__(self):
        return self.nom_de_la_campagne
    


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return self.message
# models.py

    
