# your_app/tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from leads.models import Lead  # Replace with your actual model import
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging  
from django.db.models import F

error_logger = logging.getLogger('error_logger')

@shared_task(name="send_appointment_reminder")
def send_appointment_reminder():
    try:
        
        #here right? yes
        leads = Lead.objects.filter(
            appointment_date_time__minute= F('appointment_date_time__minute') - 2,
            read_mail=False,
        )
        leads_ = Lead.objects.all()
        for l in leads_:
            print(l.appointment_date_time," -- ",l.appointment_date_time__minute, " ****  ", l.appointment_date_time__minute+2)
        
        print("****************************")
        print("Real Var") #yes are we running redis? doesnt the file doesnt matter 
        print(leads)
        for lead in leads:
            subject = "Reminder: Appointment Coming Up"
            message = f"Your appointment is coming up in 15 minutes at {lead.appointment_date_time}."
            send_mail(
                subject, message, settings.DEFAULT_FROM_EMAIL, [lead.email]
            )
            lead.read_mail = True
            lead.save(update_fields=["read_mail"])
    except:
        print('Shit Exception')
        #error_logger.info(e) #check this log
        
    return True #restart e