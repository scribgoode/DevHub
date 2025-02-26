from django.contrib import admin
from .models import Room, Message, Presence, VideoRoom

# Register your models here.
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Presence)
admin.site.register(VideoRoom) 