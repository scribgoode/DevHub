import string
import random
from django.db import models
from accounts.models import Engineer
from django.utils.timezone import now
from django.conf import settings
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from channels_presence.signals import presence_changed

channel_layer = get_channel_layer()


# A user can subscribe to many rooms, a room can be linked to many users.
# A message can belong to one user only, but a user may have many messages.
# A room may contain many messages from different users.

from uuid import uuid4

def generate_random_token(length=20):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class RoomManager(models.Manager):
    def add(self, room_channel_name, user_channel_name, user=None):
        room, _ = VideoRoom.objects.get_or_create(channel_name=room_channel_name)
        room.add_presence(user_channel_name, user)
        return room

    def remove(self, room_channel_name, user_channel_name):
        try:
            room = VideoRoom.objects.get(channel_name=room_channel_name)
        except VideoRoom.DoesNotExist:
            return
        room.remove_presence(user_channel_name)

    def prune_presences(self, channel_layer=None, age=None):
        for room in VideoRoom.objects.all():
            room.prune_presences(age)

    def prune_rooms(self):
        VideoRoom.objects.filter(presence__isnull=True).delete()  

class VideoRoom(models.Model):
    channel_name = models.CharField(
        max_length=255, unique=True, help_text="Group channel name for this room"
    )
    objects = RoomManager()

    def __str__(self):
        return self.channel_name

    def add_presence(self, channel_name, user=None):
        if user and user.is_authenticated:
            authed_user = user
        else:
            authed_user = None
            
        presence, created = Presence.objects.get_or_create(
            room=self, channel_name=channel_name, user=authed_user
        )
        if created:
            async_to_sync(channel_layer.group_add)(self.channel_name, channel_name)
            self.broadcast_changed(added=presence)

    def remove_presence(self, channel_name=None, presence=None):
        if presence is None:
            try:
                presence = Presence.objects.get(room=self, channel_name=channel_name)
            except Presence.DoesNotExist:
                return

        async_to_sync(channel_layer.group_discard)(
            self.channel_name, presence.channel_name
        )
        presence.delete()
        self.broadcast_changed(removed=presence)

    def prune_presences(self, age_in_seconds=None):
        if age_in_seconds is None:
            age_in_seconds = getattr(settings, "CHANNELS_PRESENCE_MAX_AGE", 60)

        num_deleted, _ = Presence.objects.filter(
            room=self, last_seen__lt=now() - timedelta(seconds=age_in_seconds)
        ).delete()
        if num_deleted > 0:
            self.broadcast_changed(bulk_change=True)

    def get_anonymous_count(self):
        return self.presence_set.filter(user=None).count()

    def broadcast_changed(self, added=None, removed=None, bulk_change=False):
        presence_changed.send(
            sender=self.__class__,
            room=self,
            added=added,
            removed=removed,
            bulk_change=bulk_change,
        )
 


class Room(models.Model): #this should be renamed to TextRoom
    room_id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    token = models.CharField(max_length=255, default=generate_random_token(20)) #dont think this is being used
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(Engineer, blank=True)
    roomOwner = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="room_owner", null=True, blank=True)
    roomClient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="room_client", null=True, blank=True)
    #last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_message_in_room')

    # Track if both user agreed to meeting request
    messagable = models.BooleanField(default=False) #if false, no messages can be sent in the room
    

    # def save(self, *args, **kwargs):
    #     if not self.room_id:
    #         self.room_id = uuid4()c
    #     return super(Room, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.token
    
    def get_users(self):
        return self.users.all()

    

# Message model
class Message(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="sender_user")
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="reciever_user", null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    messageContent = models.TextField()
    
    is_read = models.BooleanField(default=False) # Track if message has been read by recipient


    def get_messageContent(self):
        return self.messageContent
    
    def __str__(self):
        return self.sender.username
    
    def get_room(self):
        return self.room

    
class PresenceManager(models.Manager):
    def touch(self, channel_name):
        self.filter(channel_name=channel_name).update(last_seen=now())

    def leave_all(self, channel_name):
        for presence in self.select_related("room").filter(channel_name=channel_name):
            room = presence.room
            room.remove_presence(presence=presence)


class Presence(models.Model):
    room = models.ForeignKey("VideoRoom", on_delete=models.CASCADE)
    channel_name = models.CharField(
        max_length=255, help_text="Reply channel for connection that is present"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
    )
    last_seen = models.DateTimeField(default=now)

    objects = PresenceManager()

    def __str__(self):
        return self.channel_name

    class Meta:
        unique_together = [("room", "channel_name")]
