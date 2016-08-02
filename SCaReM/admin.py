from django.contrib import admin
from .models import *

admin.site.register(Resource)
admin.site.register(Tag)
admin.site.register(Camp)
admin.site.register(AuditLog)
admin.site.register(Reservation) # TODO - remove from admin
