from django.db import models

from accounts.models import User

class Lead(models.Model):
    date_de_soumission = models.DateField()
    nom_de_la_campagne = models.CharField(max_length=100)
    avez_vous_travaille = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
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
    qualification = models.CharField(max_length=100, choices=QUALIFICATION_CHOICES)
    comments = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
