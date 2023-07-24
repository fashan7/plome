from django.contrib import admin
from django.contrib.admin.models import LogEntry
# Register your models here.
from .models import *

admin.site.register(Lead)
admin.site.register(LogEntry)