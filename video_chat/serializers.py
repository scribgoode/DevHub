from rest_framework import serializers
from accounts.serializers import EngineerSerializer
from .models import MeetingRequest, Notification


class MeetingRequestSerializer(serializers.ModelSerializer):
    sender = EngineerSerializer()
    recipient = EngineerSerializer()
    # start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %Z")
    # end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %Z")
    #sent_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %Z")
    
    class Meta:
        model = MeetingRequest
        fields = [
            'id', 'sender', 'recipient', 'date', 'start_time', 'end_time', 
            'message', 'sent_date', 'status', 'location_name',
            'locationUpdateURL', 'type', 'lat', 'lng', 'address',
        ]

    def update(self, instance, validated_data):
        print("In update method of MeetingRequestSerializer")
        actor = self.context["request"].user
        print(f"serializer update Actor: {actor}")  # Debugging line
        # get the actor with id
        instance._actor = actor  # ⬅️ Powers the real-time notification
        return super().update(instance, validated_data)
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']