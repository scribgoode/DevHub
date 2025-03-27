
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels_presence.models import Presence, Room  #maybe this is the problem 
from django.db.models import Case, F, Q, When, Value
from django.db.models.functions import Concat, Right
from django.template.loader import render_to_string


class RtcConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.function_dict = {
            'video_chat': self._rtc,
            'join': self._join,
            'hangup': self._hangup,
        }

    @database_sync_to_async
    def _presence_connect(self, rtc_name):
        # Remove all existing connections to this room for this user.
        Presence.objects.leave_all(self.channel_name)
        self.room = Room.objects.add(rtc_name, self.channel_name, self.scope["user"]) #room is created with rtc_name but where is rtc_name defined? and this code adds the presence(channel_name) to the room

    @database_sync_to_async
    def _presence_disconnect(self, channel_name):
        Presence.objects.leave_all(channel_name)

    @database_sync_to_async
    def _presence_touch(self):
        Presence.objects.touch(self.channel_name)

    @database_sync_to_async
    def _leave_room(self, room):
        Room.objects.remove(room, self.channel_name)

    @property
    def short_name(self):
        return 'peer-'+self.channel_name[-6:]

    @property
    def user_name(self):
        return self.scope['user'].first_name or self.scope['user'].username

    def _create_self_div(self):
        return render_to_string(
            'video_chat/video_panel.html', {
                'id': f'{self.short_name}',
                'user_name': self.user_name
            }
        )

    def _create_other_div(self, occupant):
        return render_to_string(
            'video_chat/video_panel.html', {
                'id': f'{occupant["short_name"]}',
                'user_name': occupant['user_name'] #this is the user name that is referenced as {{ user_name }} on the video_panel.html
            }
        )

    async def connect(self):
        rtc_name = self.scope['url_route']['kwargs']['rtc_name'] #how does the rtc_name get passed in?
        #print(self.channel_name)
        await self._presence_disconnect(self.channel_name) #removes there channel from every room associated #connect is being ran as soon as the a new websocket is created(ws-connect= on index) and this particular line is deleting a presence if it has the same channel name
        self.rtc_call = 'rtc_%s' % rtc_name
        #print(self.rtc_call)
        await self._presence_connect(self.rtc_call)

        await self.accept()
        #print(1)
        await self.send_json({#i need to find out what is receiving this data
                'video_chat': {'type': 'connect', 'channel_name': self.channel_name} #this is the app that is trying be called. The apps object is created in tr.js and used in client.js
        })
        #print(2)
        await self.send_json({
                'html': render_to_string('video_chat/header.html', {'room': rtc_name}) #how the room name is displayed
        })
        #print(3)

    async def disconnect(self, close_code):
        # Leave room group
        await self._hangup()
        await self._presence_disconnect(self.channel_name)
        # Send "remove video" to all_but_me
        await self._all_but_me(self.rtc_call,
            {
                'type': 'rtc_message',
                'video_chat': {
                    'type': 'disconnected',
                    'channel_name': self.channel_name,
                },
            }
        )

    # Receive message from WebSocket
    async def receive_json(self, content):
        await self._presence_touch()
        #print(content, "print statement in receive_josn function in consumer.py") #this function does not receive data from send_json in this file

        for message_key, message_value in content.items():
            if message_key in self.function_dict:
                #print(message_key, message_value, "message_key and message_value in receive_json function in consumer.py")
                await self.function_dict[message_key](message_value)

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

    async def _join(self, rtc_call):
        #print(rtc_call, "rtc_call in _join function in consumer.py")
        #print(self.rtc_call, "self.rtc_call in _join function in consumer.py")
        if self.rtc_call:
            await self._leave_room(self.rtc_call)

        self.rtc_call = rtc_call
        await self.send_json({
                'html': render_to_string('video_chat/header.html', {'room': rtc_call})
        })

        # Send list of connected peers (occupants) to self
        occupants = await self._room_occupants(self.rtc_call) #this is where the occupants are defined
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

    async def rtc_message(self, event):
        # Send message to WebSocket
        #print(event, 'helloooooooooo') 
        await self.send_json({
            'video_chat': event['video_chat'] #not sure how rtc_message is being called or what the event parameter is
        })

    async def html_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)
