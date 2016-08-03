from django.contrib import admin
from .models import Resource, Tag, Camp, Reservation

admin.site.register(Resource)
admin.site.register(Tag)
admin.site.register(Camp)
admin.site.register(Reservation)  # TODO - remove from admin
