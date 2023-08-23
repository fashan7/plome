# import os
# from celery import Celery

# from datetime import timedelta

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CRM.settings")

# app = Celery("CRM")

# app.config_from_object(
#     "django.conf:settings",
# )

# app.autodiscover_tasks()


# app.conf.beat_schedule = {
#     "send_appointment_reminder": {
#         "task": "send_appointment_reminder",
#         "schedule": timedelta(seconds=10),
#     },
# }