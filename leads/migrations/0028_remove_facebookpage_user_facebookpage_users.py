# Generated by Django 4.2.4 on 2023-09-07 15:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leads', '0027_remove_facebookpage_users_facebookpage_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facebookpage',
            name='user',
        ),
        migrations.AddField(
            model_name='facebookpage',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
