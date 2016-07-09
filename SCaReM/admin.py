from django.contrib import admin
from .models import Tag
from .models import Resource

admin.site.register(Resource)
admin.site.register(Tag)
