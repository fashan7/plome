# myapp/management/commands/run_scheduler.py

from django.core.management.base import BaseCommand
from schedule import every
from datetime import timedelta
import schedule
import time
from leads.fetch_sales_leads_periodic import Command as FetchSalesLeadsPeriodicCommand

class Command(BaseCommand):
    help = 'Run scheduled tasks'

    def handle(self, *args, **kwargs):
        # Create an instance of your custom management command
        fetch_sales_leads_periodic_command = FetchSalesLeadsPeriodicCommand()

        # Schedule the custom command to run periodically
        schedule.every(timedelta(minutes=5)).do(fetch_sales_leads_periodic_command.handle)

        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)
