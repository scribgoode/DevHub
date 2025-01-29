import json
from django.shortcuts import get_object_or_404
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models import Q

from .models import Room, Message
from accounts.models import Engineer

#
# ChatConsumer Class: This class inherits from WebsocketConsumer, which is provided by Channels for handling WebSocket connections.
#
class ChatConsumer(WebsocketConsumer):
    def connect(self): # When a new WebSocket connection is made, this method is called.
        self.profile_id = self.scope["url_route"]["kwargs"]["profile_id"]
        profile_user = get_object_or_404(Engineer, id=self.profile_id)
        current_user = self.scope["user"]

        print("profile_user: ", profile_user)
        if profile_user is not None:
            users = [profile_user, self.scope["user"]]
        # Query to find a room that includes both profile_user and current_user

        room_qs = Room.objects.filter(users=profile_user).filter(users=current_user)
        #print("room_qs: ", room_qs)
        if not room_qs.exists():
            new_chatroom = Room.objects.create()
            new_chatroom.users.add(profile_user, current_user)
            new_chatroom.roomOwner = profile_user
            new_chatroom.roomClient = current_user
            new_chatroom.save()
            self.room = new_chatroom
        else:
            self.room = room_qs.first()

        self.room_group_name = self.room.token

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.accept())

    def disconnect(self, close_code): # When the WebSocket connection is closed, this method is called.
        #pass 
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        
    def receive(self, text_data): # When the WebSocket connection receives a message, this method is called.
        # receive is called first
        text_data_json = json.loads(text_data)
        print("text_data_json: ", text_data_json)
        # Create a new message instance and save it to the database
        
        message = Message.objects.create(
            room=self.room,
            sender=self.scope["user"],
            messageContent=text_data_json["message"]
        )
        async_to_sync(message.save())

        # send data to send_message()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "msgObj": text_data_json}
        )

    def chat_message(self, event): # This method sends the message to the WebSocket connection.
        # recieve data from receive()
        msgObj = event["msgObj"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": msgObj["message"],
            "sender": msgObj["sender"],
            "sender_full_name": msgObj["sender_full_name"],
            "sender_id": msgObj["sender_id"]
        }))