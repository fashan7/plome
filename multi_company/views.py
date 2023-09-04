# multi_company/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import CustomUserTypes

from django.shortcuts import render
from .models import Company  # Import the Company model
def company_dropdown_view(request):
    companies = Company.objects.all()
    return {'companies': companies}