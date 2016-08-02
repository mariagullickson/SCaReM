from django.shortcuts import render
from models import Camp, Resource, AuditLog
from datetime import datetime, timedelta

def index(request, errors=None):
    data = {
        'camps': Camp.objects.all(),
        'resources': Resource.objects.all(),
        'error_messages': errors
        }
    return render(request, 'index.html', data)

def log(request, year=None, month=None, day=None):
    if year:
        start_year = int(year)
        start_month = int(month) if month else 1
        start_day = int(day) if day else 1
        start_date = datetime(start_year, start_month, start_day)
        if day:
            end_date = start_date + timedelta(1)
        elif month:
            if start_month == 12:
                end_month = 1
                end_year = start_year + 1
            else:
                end_month = start_month + 1
                end_year = start_year
            end_date = datetime(end_year, end_month, 1)
        else:
            end_date = datetime(start_year + 1, 1, 1)
                
        logs = AuditLog.objects.filter(timestamp__gte=start_date) \
                               .filter(timestamp__lt=end_date) \
                               .order_by('timestamp')
    else:
        logs = AuditLog.objects.all().order_by('timestamp')
    data = {
        'logs': logs
    }
    return render(request, 'logs.html', data)
