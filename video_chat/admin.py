from django.contrib import admin
from channels_presence.models import Presence, Room
# Register your models here.

admin.site.register(Presence)
admin.site.register(Room)
