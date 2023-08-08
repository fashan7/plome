# Generated by Django 4.2.2 on 2023-08-08 06:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0005_remove_lead_nom_remove_lead_prenom_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='lead_attachments/')),
                ('title', models.CharField(max_length=100)),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='leads.lead')),
            ],
        ),
    ]
