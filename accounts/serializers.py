from rest_framework import serializers
from text_chat.models import Room, Message
from accounts.models import Engineer

class EngineerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engineer
        fields = (
            'first_name',
            'last_name',
            'email',
            'id',
        )

class RoomSerializer(serializers.ModelSerializer):
    users = EngineerSerializer(many=True)
    class Meta:
        model = Room
        fields = (
            'users',
            'roomOwner',
            'roomClient',
            'token',
            'room_id', 
        )

class MessageSerializer(serializers.ModelSerializer):
    sender = EngineerSerializer()
    class Meta:
        model = Message
        fields = (
            'sender',
            'messageContent',
            'timestamp',
            'room_id',
        )