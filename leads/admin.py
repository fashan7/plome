from django.contrib import admin
from django.contrib.admin.models import LogEntry
# Register your models here.
from .models import *

admin.site.register(Lead)

admin.site.register(Notification)
admin.site.register(LogEntry)
admin.site.register(FacebookLead)
admin.site.register(LeadHistory)


admin.site.register(LogEntry)
admin.site.register(Notification)

admin.site.register(Attachment)


