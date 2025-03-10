from rest_framework import serializers
from accounts.serializers import EngineerSerializer
from .models import MeetingRequest

class MeetingRequestSerializer(serializers.ModelSerializer):
    sender = EngineerSerializer()
    recipient = EngineerSerializer()
    class Meta:
        model = MeetingRequest
        fields = '__all__'