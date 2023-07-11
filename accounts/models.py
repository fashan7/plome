from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.conf import settings

User = settings.AUTH_USER_MODEL 

class CustomUserTypes(AbstractUser):
    is_sales = models.BooleanField(default = False)
    is_advisor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)





    # is_superadmin = models.BooleanField(default = False)