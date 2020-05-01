from django.contrib import admin
from django.apps import apps
from Message.models import *


admin.site.register(Persons)
admin.site.register(Message_room)
admin.site.register(Messages)

# Register your models here.