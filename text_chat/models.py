import string
import random
from django.db import models
from accounts.models import Engineer


def generate_random_string(length):
    random_string = "".join(random.choice(string.ascii_letters) for _ in range(length))
    return random_string

# Room model
class Room(models.Model):
    token = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(Engineer)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_random_string(20)
        return super(Room, self).save(*args, **kwargs)

# Message model
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        Engineer, on_delete=models.CASCADE, related_name="sender_user"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.sender.username
    