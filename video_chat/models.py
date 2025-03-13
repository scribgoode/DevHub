from django.db import models
from accounts.models import Engineer
from text_chat.models import Room
from meetup_point.models import Address
import string
import random
# Create your models here.

def generate_random_token(length=20):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class Meeting(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='recipient')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'upcoming'
        ONGOING = 'ongoing', 'ongoing'
        COMPLETED = 'completed', 'completed'
        CANCELLED = 'cancelled', 'cancelled'
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.UPCOMING)
    type = models.CharField(max_length=50)
    #room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room')
    #create the room as soon the meeting is created
    #create room token regardless of the meeting type
    room_token = models.CharField(max_length=255, default=generate_random_token(20))
    meeting_request = models.ForeignKey('MeetingRequest', on_delete=models.CASCADE, related_name='meeting_request', null=True, blank=True)

#we need to be sure but we may only need a meeting model for meetings and meeting requests as long as we have enough switches
class MeetingRequest(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_sender')
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_recipient')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    class Status(models.TextChoices):
        PENDING = 'pending', 'pending'
        ACCEPTED = 'accepted', 'accepted'
        REJECTED = 'rejected', 'rejected'
        CANCELLED = 'cancelled', 'cancelled'
    status = models.CharField(max_length=50, default=Status.PENDING, choices=Status.choices)
    location_name = models.CharField(max_length=255, default='') # either url or address string
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    locationUpdateURL = models.CharField(max_length=255, default='', null=True, blank=True)
    class Type(models.TextChoices):
        INPERSON = 'in-person', 'in-person'
        VIDEO = 'video', 'video'
        TEXT = 'text', 'text'
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.INPERSON)

# serializers.py
from rest_framework import serializers
from accounts.serializers import EngineerSerializer
from .models import MeetingRequest

class MeetingRequestSerializer(serializers.ModelSerializer):
    sender = EngineerSerializer()
    recipient = EngineerSerializer()
    
    class Meta:
        model = MeetingRequest
        fields = [
            'id', 'sender', 'recipient', 'date', 'start_time', 'end_time', 
            'message', 'sent_date', 'status', 'location_name',
            'locationUpdateURL', 'type'
        ]