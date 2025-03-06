from django.db import models
from accounts.models import Engineer
from text_chat.models import Room
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
    status = models.CharField(max_length=50, default='upcoming')
    type = models.CharField(max_length=50)
    #room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room')
    #create the room as soon the meeting is created
    #create room token regardless of the meeting type
    room_token = models.CharField(max_length=255, default=generate_random_token(20))

class MeetingRequest(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_sender')
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_recipient')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    class Type(models.TextChoices):
        INPERSON = 'in-person', 'in-person'
        VIDEO = 'video', 'video'
        TEXT = 'text', 'text'
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.INPERSON)