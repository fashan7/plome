from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(PageAllocation)
admin.site.register(Privilege)