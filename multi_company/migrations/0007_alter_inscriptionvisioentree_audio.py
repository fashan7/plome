# Generated by Django 4.2.4 on 2023-09-13 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multi_company', '0006_alter_doisser_criteres_com_alter_doisser_numero_edof_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscriptionvisioentree',
            name='audio',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
