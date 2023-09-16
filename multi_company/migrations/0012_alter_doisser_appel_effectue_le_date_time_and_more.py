# Generated by Django 4.2.4 on 2023-09-13 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multi_company', '0011_alter_doisser_appel_effectue_le_date_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doisser',
            name='appel_effectue_le_date_time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='date_dinscription',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='date_prevue_d_entree_en_formation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='date_prevue_de_fin_de_formation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='inscription_visio_entree_colis_a_envoyer_le',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='inscription_visio_entree_date_d_encaissement',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='inscription_visio_entree_date_de_facturation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='doisser',
            name='rdv_confirme_dateandtime',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]