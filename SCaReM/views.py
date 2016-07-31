from django.shortcuts import render
import models

def index(request, errors=None):
    data = {
        'camps': models.Camp.objects.all(),
        'resources': models.Resource.objects.all(),
        'error_messages': errors
        }
    return render(request, 'index.html', data)
