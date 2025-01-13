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

        # self.send(text_data=json.dumps({
        #     'type': "connection_established",
        #     'message': 'Hello World!'
        #     }))
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # try:
        #     target_user = get_object_or_404(Engineer, username=self.room_name)
        # except:
        #     target_user = ""
        # if target_user is not None:
        #     users = [target_user, self.scope["Engineer"]]
        #     room_qs = Room.objects.filter(users=target_user).filter(
        #         users=self.scope["Engineer"]
        #     )
        #     if not room_qs.exists():
        #         self.room = Room.objects.create()
        #         self.room.users.set(users)
        #     else:
        #         self.room = room_qs.first()
        #     self.room_group_name = self.room.token

        self.room_name = self.scope["url_route"]["kwargs"]["profile_id"]
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code): # When the WebSocket connection is closed, this method is called.
        #pass 
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        
    def receive(self, text_data): # When the WebSocket connection receives a message, this method is called.
        # receive is called first
        text_data_json = json.loads(text_data)

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
            "sender_id": msgObj["sender_id"],
        }))