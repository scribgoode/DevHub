from rest_framework import serializers
from text_chat.models import Room, Message
from accounts.models import Engineer
from meetup_point.models import Address
from cities_light.models import City, Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = City
        fields = ['id', 'name', 'country']

class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    country = CountrySerializer()

    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country', 'lat', 'lng']

class EngineerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Engineer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'status', 'projects', 'dob', 'country', 'city', 'elevator_pitch', 'address', 'rating', 'rating_count', 'NumMeetings', 'NumInPersonMeetings', 'NumVideoMeetings', 'meeting_preference']

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