# Generated by Django 4.1.1 on 2023-07-12 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_alter_lead_avez_vous_travaille'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='qualification',
            field=models.CharField(choices=[('nrp1', 'NRP1'), ('nrp2', 'NRP2'), ('nrp3', 'NRP3'), ('en_cours', 'En cours'), ('rappel', 'Rappel'), ('faux_numero', 'Faux numéro'), ('pas_de_budget', 'Pas de budget'), ('pas_interesse', 'Pas intéressé'), ('ne_pas_rappele', 'Ne pas rappeler'), ('signe_pole_emploi', 'Signé Pôle Emploi'), ('signe_cpf', 'Signé CPF')], default=1, max_length=100),
            preserve_default=False,
        ),
    ]