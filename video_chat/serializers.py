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
            'locationUpdateURL', 'type', 'lat', 'lng', 'address',
        ]
