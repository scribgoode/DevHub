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

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Restrict access to authenticated users
def get_meeting_requests_by_sender_and_recipient(request):
    print(f"User: {request.user}, Auth: {request.auth}")  # Debug authentication
    sender_id = request.GET.get('sender')
    recipient_id = request.GET.get('recipient')

    if sender_id and recipient_id:
        meeting_requests = MeetingRequest.objects.filter(sender_id=sender_id, recipient_id=recipient_id, type=MeetingRequest.Type.INPERSON)
        serializer = MeetingRequestSerializer(meeting_requests, many=True)
        return Response(serializer.data)
    else:
        return Response({"error": "Both sender and recipient IDs are required."}, status=400)
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # Restrict access to authenticated users
def update_meeting_request(request, pk):
    try:
        meeting_request = MeetingRequest.objects.get(pk=pk)
    except MeetingRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MeetingRequestSerializer(meeting_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)