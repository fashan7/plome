# from celery import shared_task
# from datetime import datetime, timedelta
# from leads.models import Lead  
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils import timezone
# import logging  
# from django.db.models import Q
# import pytz

# error_logger = logging.getLogger('error_logger')

# @shared_task(name="send_appointment_reminder")
# def send_appointment_reminder():
#     try:
        
        
        
#         paris_timezone = pytz.timezone('Europe/Paris')
#         current_time_paris = timezone.now().astimezone(paris_timezone)
#         current_time_paris_rounded = current_time_paris.replace(second=0, microsecond=0)

#         reminder_time = current_time_paris_rounded + timedelta(minutes=2)


#         # leads_ = Lead.objects.filter(
#         #     read_mail=False,
#         # )
#         # for l in leads_:
#         #     print(l.appointment_date_time)
            
#         #     print(reminder_time - timedelta(minutes=2))
#         #     print(reminder_time)

#         #     reminder_time_without_offset = reminder_time.replace(tzinfo=None)
#         #     appointment_time_without_offset = l.appointment_date_time.replace(tzinfo=None)
#         #     print(reminder_time_without_offset)
#         #     print(appointment_time_without_offset)
#         # #     print(l.appointment_date_time.minute)
#         # #     print(current_time_paris)
#         # #     print(current_time_paris_rounded)
#         #     # print(reminder_threshold_end)

#         leads = Lead.objects.filter(
#             appointment_date_time=reminder_time.replace(tzinfo=None)  - timedelta(minutes=2),
#             read_mail=False,
#         )

#         print("****************************")
#         print("Real Var")
#         print(leads)
#         for lead in leads:
#             subject = "Reminder: Appointment Coming Up"
#             message = f"Your appointment is coming up in 15 minutes at {lead.appointment_date_time}."
#             send_mail(
#                 subject, message, settings.DEFAULT_FROM_EMAIL, [lead.email]
#             )
#             lead.read_mail = True
#             lead.save(update_fields=["read_mail"])
#     except Exception as e:
#         error_logger.info(e) #check this log
        
#     return True #restart e