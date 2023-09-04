from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from multi_company.models import Company

User = settings.AUTH_USER_MODEL 

class CustomUserTypes(AbstractUser):
    is_sales = models.BooleanField(default = False)
    is_advisor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=True, blank=True)




    # is_superadmin = models.BooleanField(default = False)