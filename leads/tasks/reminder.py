# your_app/tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from leads.models import Lead  # Replace with your actual model import
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging  

error_logger = logging.getLogger('error_logger')

@shared_task(name="send_appointment_reminder")
def send_appointment_reminder():
    try:
        leads = Lead.objects.filter(
            appointment_date_time__minute=timezone.now().minute - 15,
            read_mail=False,
        )

        for lead in leads:
            subject = "Reminder: Appointment Coming Up"
            message = f"Your appointment is coming up in 15 minutes at {lead.appointment_date_time}."
            send_mail(
                subject, message, settings.DEFAULT_FROM_EMAIL, [lead.email]
            )
            lead.read_mail = True
            lead.save(update_fields=["read_mail"])
    except Exception as e:
        error_logger.info(e)
    return True