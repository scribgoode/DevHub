import json
from django.shortcuts import get_object_or_404
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Q, F, Case, When, Value
from django.db.models.functions import Concat, Right
from .models import Room, Message, Presence, VideoRoom
from accounts.models import Engineer
from django.template.loader import render_to_string
from channels.db import database_sync_to_async



#
# ChatConsumer Class: This class inherits from WebsocketConsumer, which is provided by Channels for handling WebSocket connections.
#
class ChatConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_dict = {
            'video_chat': self._rtc,
            'join': self._join,
            'hangup': self._hangup,
        }
    
    @database_sync_to_async
    def _leave_room(self, room):
        VideoRoom.objects.remove(room, self.channel_name)

    @database_sync_to_async
    def _presence_connect(self, rtc_name):
        # Remove all existing connections to this room for this user.
        Presence.objects.leave_all(self.channel_name)
        self.room = VideoRoom.objects.add(rtc_name, self.channel_name, self.scope["user"]) #room is created with rtc_name but where is rtc_name defined? and this code adds the presence(channel_name) to the room
    
    # @database_sync_to_async
    # def _presence_disconnect(self, channel_name):
    #     Presence.objects.leave_all(channel_name)

    @database_sync_to_async
    def _presence_touch(self):
        Presence.objects.touch(self.channel_name)

    async def _hangup(self, hangup=None):
        await self._leave_room(self.rtc_call)

        await self._all_but_me(self.rtc_call,
            {
                'type': 'rtc_message',
                'video_chat': {
                    'type': 'disconnected',
                    'channel_name': self.channel_name,
                }
            }
        )
        self.rtc_call = None    

    async def _all_but_me(self, room, message):
        occupants = await self._room_occupants(room)
        '''
        if occupants:
            print(occupants)
        
        if message:
            print(message, "message in _all_but_me function in consumer.py")
        '''
        for occupant in occupants:
            if occupant['channel_name'] != self.channel_name:
                await self.channel_layer.send(
                    occupant['channel_name'], message
                )

    async def html_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)    

    async def rtc_message(self, event):
        # Send message to WebSocket
        #print(event, 'helloooooooooo') 
        await self.send_json({
            'video_chat': event['video_chat'] #not sure how rtc_message is being called or what the event parameter is
        })


    @database_sync_to_async
    def _room_occupants(self, room):
        return list(Presence.objects.filter(
            room__channel_name=room
        ).annotate(
            user_name=Case(
                When(~Q(user__first_name=''), then=F('user__first_name')), #this is where the user name is defined
                default=F('user__username')
            ),
            short_name=Concat(Value('peer-'), Right('channel_name', 6))  #this is where the room id is created
        ).values('channel_name', 'user_name', 'short_name'))
    
    def _create_self_div(self):
        return render_to_string(
            'video_chat/video_panel.html', {
                'id': f'{self.short_name}',
                'user_name': self.user_name
            }
        )
    
    async def grabProfile(self, profile_id):
        get_user = sync_to_async(Engineer.objects.get)
        self.profile_user = await get_user(id=profile_id)
    
    async def roomExists(self):
        #check_room_exists = sync_to_async(self.room_qs.exists())
        self.room_exists = await self.room_qs.aexists()
    
    async def createTextRoom(self):
        create_room = sync_to_async(Room.objects.create)
        self.new_chatroom = await create_room()
        
    async def addUsersToRoom(self):
        add_users = sync_to_async(self.new_chatroom.users.add)
        await add_users(self.profile_user, self.current_user)
    
    async def get_token(self):
        return self.new_chatroom.token

    async def createMessage(self, message):
        print(message, "message in createMessage function in consumer.py")
        create_message = sync_to_async(Message.objects.create)
        self.message = await create_message(
            room=self.new_chatroom,
            sender=self.scope["user"],
            recipient=self.profile_user,
            messageContent=message
        )
        #print(self.message, "self.message in createMessage function in consumer.py")
        await self.message.asave()
    
    
    
    @property
    def short_name(self):
        return 'peer-'+self.channel_name[-6:]

    @property
    def user_name(self):
        return self.scope['user'].first_name or self.scope['user'].username

    def _create_other_div(self, occupant):
        return render_to_string(
            'video_chat/video_panel.html', {
                'id': f'{occupant["short_name"]}',
                'user_name': occupant['user_name'] #this is the user name that is referenced as {{ user_name }} on the video_panel.html
            }
        )


    # async def connect(self): # When a new WebSocket connection is made, this method is called.
    #     self.profile_id = self.scope["url_route"]["kwargs"]["profile_id"]
    #     #profile_user = get_object_or_404(Engineer, id=self.profile_id)
    #     #profile_user = Engineer.objects.get(id=self.profile_id)
    #     await self.grabProfile()
    #     self.current_user = self.scope["user"]
    #     #why cant i just have two different consumers?
        
    #     print("profile_user: ", self.profile_user)
    #     # Query to find a room that includes both profile_user and current_user

    #     self.room_qs = Room.objects.filter(users=self.profile_user).filter(users=self.current_user)
    #     #print("room_qs: ", room_qs)
    #     await self.roomExists()
    #     if not self.room_exists:
    #         new_chatroom = Room.objects.create()
    #         new_chatroom.users.add(self.profile_user, self.current_user)
    #         new_chatroom.roomOwner = self.profile_user
    #         new_chatroom.roomClient = self.current_user
    #         new_chatroom.save()
    #         self.room = new_chatroom
    #     else:
    #         self.room = await self.room_qs.afirst()
        

    #     self.room_group_name = self.room.token

    #     # Join room group
    #     await self.channel_layer.group_add(
    #         self.room_group_name,
    #         self.channel_name
    #     )
    #     #self.channel_layer.group_add(self.room_group_name, self.channel_name)

    #     await self.accept()
    #     #self.accept()

    async def grabChatRoom(self, profile_id):
        await self.grabProfile(profile_id)
        self.current_user = self.scope["user"]
        self.room_qs = Room.objects.filter(users=self.profile_user).filter(users=self.current_user)
        await self.roomExists()
        if not self.room_exists:
            await self.createTextRoom()
            await self.addUsersToRoom() #left off here probably just should have made two different consumers but not necessarlily because you probably would have need two websocket connections open
            self.new_chatroom.roomOwner = self.profile_user
            self.new_chatroom.roomClient = self.current_user
            await self.new_chatroom.asave()
            #self.room = new_chatroom 
        else:
            #self.room = self.room_qs.afirst()
            self.new_chatroom = await self.room_qs.afirst()
        

        self.room_group_name = await self.get_token()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
    async def connect(self):
        self.endpoint_name = self.scope['url_route']['kwargs']['chat_type']
        self.rtc_call = "video" #this needs to be left for now
        self.current_user = self.scope["user"]
        self.user_group = f'user_{self.current_user.id}'

        await self.change_status()

        print("🔌 Adding user to group:", self.user_group)

        await self.channel_layer.group_add(self.user_group, self.channel_name)

        await self.accept()

        if self.endpoint_name == 'video':
            await self.send_json({#i need to find out what is receiving this data
                    'video_chat': {'type': 'connect', 'channel_name': self.channel_name} #this is the app that is trying be called. The apps object is created in tr.js and used in client.js
            }) 

    # async def disconnect(self, close_code): # When the WebSocket connection is closed, this method is called.
    #     # Leave room group
    #     await self._hangup()
    #     await self._presence_disconnect(self.channel_name)
    #     # Send "remove video" to all_but_me
    #     await self._all_but_me(self.rtc_call,
    #         {
    #             'type': 'rtc_message',
    #             'video_chat': {
    #                 'type': 'disconnected',
    #                 'channel_name': self.channel_name,
    #             },
    #         }
    #     )

    #     await self.channel_layer.group_discard(
    #         self.room_group_name, self.channel_name 
    #     )
    
    async def receive_json(self, content):
        await self._presence_touch()
        #print(content, "print statement in receive_josn function in consumer.py") #this function does not receive data from send_json in this file

        for message_key, message_value in content.items():
            if message_key == "text":
                await self.send_message(message_value)

            if message_key == "profile_id":
                await self.grabChatRoom(message_value)

            if message_key == "room_token":
                #print(message_value, "message_value in receive_json function in consumer.py")
                self.room_token = message_value
                await self._presence_connect(self.room_token)

            if message_key in self.function_dict:
                #print(message_key, message_value, "message_key and message_value in receive_json function in consumer.py")
                await self.function_dict[message_key](message_value)

    async def send_message(self, content):
        #text_data_json = json.loads(content)
        #print("text_data_json: ", content)
        # Create a new message instance and save it to the database
        
        await self.createMessage(content["message"])

        # send data to send_message()
        #print(self.room_group_name, "self.channel_layer in send_message function in consumer.py")
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "msgObj": content} #chat_message receives this
        )

        
    # def receive(self, text_data): # When the WebSocket connection receives a message, this method is called.
    #     # receive is called first
    #     text_data_json = json.loads(text_data)
    #     print("text_data_json: ", text_data_json)
    #     # Create a new message instance and save it to the database
        
    #     message = Message.objects.create(
    #         room=self.room,
    #         sender=self.scope["user"],
    #         messageContent=text_data_json["message"]
    #     )
    #     async_to_sync(message.save())

    #     # send data to send_message()
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name, {"type": "chat.message", "msgObj": text_data_json}
    #     )

    async def chat_message(self, event): # This method sends the message to the WebSocket connection.
        # recieve data from receive()
        msgObj = event["msgObj"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": msgObj["message"],
            "sender": msgObj["sender"],
            "sender_full_name": msgObj["sender_full_name"],
            "sender_id": msgObj["sender_id"]
        }))
        #print("sent: ", msgObj) 

    async def _join(self, rtc_call):
        #print(rtc_call, "rtc_call in _join function in consumer.py")
        #print(self.rtc_call, "self.rtc_call in _join function in consumer.py")
        if self.rtc_call:
            await self._leave_room(self.rtc_call)

        self.rtc_call = rtc_call
        # Send list of connected peers (occupants) to self
        occupants = await self._room_occupants(self.rtc_call) #this is where the occupants are defined
        #print(occupants, "occupants in _join function in consumer.py")
        #if occupants:
            #print(occupants)
        all_divs = "\n".join([
            self._create_other_div(occupant)
            for occupant in occupants
            if occupant['channel_name'] != self.channel_name
        ])

        #NOTE: The html must be sent before the connections
        # Otherwise, the connection functions in the client
        # will be trying to access the div before it exists

        await self.send_json({
                'html': all_divs
        })
        await self.send_json({ #what is this doing? its calling the function in the client.js
                'video_chat': {
                    'type': 'others',
                    'ids': occupants,
                },
        })

        await self._all_but_me(self.rtc_call,
            {
                'type': 'html_message',
                'html': self._create_self_div()
            }
        )

        # Send self.channel_name to all connected peers
        await self._all_but_me(self.rtc_call,
            {
                'type': 'rtc_message',
                'video_chat': {
                    'type': 'other',
                    'channel_name': self.channel_name,
                    'user_name': self.user_name,
                    'short_name': self.short_name
                },
            }
        )

        await self._presence_connect(self.rtc_call)

    async def _rtc(self, rtc):
        # If there's a recipient, send to it.
        if 'recipient' in rtc:
            #print(rtc, "rtc in _rtc function in consumer.py")
            #print(self.channel_layer, "self.channel_name in _rtc function in consumer.py")
            await self.channel_layer.send(
                rtc['recipient'], {
                    'type': 'rtc_message',
                    'video_chat': rtc,
                }
            )
        else:
            await self._all_but_me(
                self.rtc_call, {
                    'type': 'rtc_message',
                    'video_chat': rtc
                }
            )
        #print("sent to recipient")

    async def notification_message(self, event):
        print("📩 Notification message received in consumer")  # ← DEBUG PRINT
        print("📩 Consumer received event:", event)
        await self.send_json({
            'notification': {
                'sender': event['sender'],
                'id': event['id'],
                'message': event['message'],
                'created_at': event['created_at'],
                'type': event.get('notification_type', 'request'),
            }
        })
    
    async def change_status(self):
        self.current_user.online_status = True
        await self.current_user.asave()
    
    async def disconnect(self, close_code): # When the WebSocket connection is closed, this method is called.
        await Presence.objects.filter(user=self.current_user, room=self.room).adelete()
        await self.current_user.asave()