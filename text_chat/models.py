import string
import random
from django.db import models
from accounts.models import Engineer


# A user can subscribe to many rooms, a room can be linked to many users.
# A message can belong to one user only, but a user may have many messages.
# A room may contain many messages from different users.

from uuid import uuid4

def generate_random_token(length=20):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Room model
class Room(models.Model):
    room_id = models.UUIDField(primary_key=True, unique=True, default=uuid4(), editable=False)
    token = models.CharField(max_length=255, default=generate_random_token(20))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(Engineer, blank=True)
    roomOwner = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="room_owner", null=True, blank=True)
    roomClient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="room_client", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = models.UUIDField(primary_key=True, unique=True, default=uuid4(), editable=False)
        return super(Room, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.token
    
    def get_users(self):
        return self.users.all()

    

# Message model
class Message(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="sender_user")
   #reciever = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="reciever_user", null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    messageContent = models.TextField()


    def get_messageContent(self):
        return self.messageContent
    
    def __str__(self):
        return self.sender.username
    
    def get_room(self):
        return self.room
    







    #token = models.CharField(max_length=255, unique=True)
    # users = models.ManyToManyField(Engineer)
    # def save(self, *args, **kwargs):
    #     if not self.token:
    #         #self.token = generate_random_string(20)
    #     return super(Room, self).save(*args, **kwargs)
    
    # roomDic = {}
    # def get_chat(self, engineer1, engineer2):
    #     if (engineer1, engineer2) in self.roomDic:
    #         return self.roomDic[(engineer1, engineer2)]
    #     else:
    #         return None
    # def set_chat(self, engineer1, engineer2, chat):
    #     self.roomDic[(engineer1, engineer2)] = chat




# room -


# class chatHistory(models.Model):
    
# Message model
# class Message(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     sender = models.ForeignKey(
#         Engineer, on_delete=models.CASCADE, related_name="sender_user"
#     )
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return self.sender.username
    