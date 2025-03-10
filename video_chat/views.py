from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from .models import MeetingRequest
from .serializers import MeetingRequestSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

class MeetingRequestViewSet(viewsets.ModelViewSet):
    queryset = MeetingRequest.objects.all()
    serializer_class = MeetingRequestSerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def meeting_requests_list(request):
    meetings = MeetingRequest.objects.all()
    serializer = MeetingRequestSerializer(meetings, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only authenticated users can create a meeting request
def create_meeting_request(request):
        print("here")
    #try:
        # Create a new MeetingRequest object
        # new_meeting_request = MeetingRequest(
        #     sender=request.data['sender'],
        #     recipient=request.data['recipient'],
        #     date=request.data['date'],
        #     start_time=request.data['start_time'],
        #     end_time=request.data['end_time'],
        #     message=request.data['message'],
        #     type=request.data['type']
        # )
        # new_meeting_request.save()
        return Response(status=status.HTTP_201_CREATED)
    # except:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)