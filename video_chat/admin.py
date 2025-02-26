from django.contrib import admin
#from channels_presence.models import Presence, Room
from .models import Meeting, MeetingRequest
# Register your models here.

#admin.site.register(Presence)
#admin.site.register(Room)
admin.site.register(Meeting)
admin.site.register(MeetingRequest)