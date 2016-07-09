from django.http import HttpResponse

def index(request):
    return HttpResponse('Hello World!')

def tags(request):
    return HttpResponse('Hello tags')
