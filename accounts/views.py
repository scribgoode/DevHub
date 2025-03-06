from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Engineer
from cities_light.models import City
from text_chat.models import Room, Message
from video_chat.models import Meeting, MeetingRequest
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from accounts.serializers import EngineerSerializer, RoomSerializer, MessageSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from video_chat.forms import MeetingRequestForm
from django.contrib import messages
from accounts.forms import ElevatorPitchForm
'''
class HomePageView(TemplateView):
    template_name = "home.html"
'''

def home(request):
    if 'search' in request.GET:
        search = request.GET['search']
        profiles = Engineer.objects.filter(Q(first_name__icontains=search) | Q(current_project__icontains=search))
    elif 'city' in request.GET:
        city = request.GET['city']
        profiles = Engineer.objects.filter(city__name=city)
    elif 'option' in request.GET:
        status = request.GET['option']
        if status == 'any':
            profiles = Engineer.objects.all()
        else:
            profiles = Engineer.objects.filter(status=status)
    else:
        profiles = Engineer.objects.all()
    
    cities = City.objects.all()
    context = {'profiles': profiles,
               'cities': cities,}
    return render(request, 'home.html', context)

def Profile(request, id):
    if request.method == 'POST':
        meeting_request_form = MeetingRequestForm(request.POST)
        if MeetingRequest.objects.filter(sender=request.user, recipient=Engineer.objects.get(id=id), status="pending").exists():
            messages.warning(request, 'You already have a meeting request pending for this user. You have to wait until they accept, decline, or the date has passed.')
        elif meeting_request_form.is_valid():
            meeting_request = meeting_request_form.save(commit=False)
            meeting_request.sender = request.user
            meeting_request.recipient = Engineer.objects.get(id=id)
            meeting_request.save()
    else:
        meeting_request_form = MeetingRequestForm()
        
    profile = Engineer.objects.get(id=id)
    context = {'profile': profile,
               'form': meeting_request_form,}
    return render(request, 'profile.html', context)

def myProfile(request):
    if request.method == 'POST':
        form_type = request.POST.get("form_type")
        print(form_type)
        if form_type ==  "meeting_request_decision":
            meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
            meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message)
            meeting.save()
            meeting_request.status = 'resolved'
            meeting_request.save()
        if form_type == "video_upload":
            user = request.user
            user.elevator_pitch = request.FILES['elevator_pitch']
            user.save()
        if form_type == "video_remove":
            user = request.user
            user.elevator_pitch.delete()

    meetings = Meeting.objects.filter( Q(recipient=request.user) | Q(sender=request.user) )
    meeting_requests = MeetingRequest.objects.filter( Q(recipient=request.user) | Q(sender=request.user) ) #maybe make meeting_requests and sent_meetings_requests
    context = {'meetings': meetings,
               'meeting_requests': meeting_requests,}

    return render(request, 'my_profile.html', context)

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def profile_list(request):
    profiles = Engineer.objects.all()
    serializer = EngineerSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def profile_detail(request, pk):
    profile = get_object_or_404(Engineer, pk=pk)
    serializer = EngineerSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def room_list(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_room(request, pk):
    rooms = Room.objects.filter(users__id=pk)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def message_list(request):
    message_list = Message.objects.all()
    serializer = MessageSerializer(message_list, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_chat(request, pk):
    messages = Message.objects.filter(room_id=pk)
    print(messages)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

#this is apart of testing for the implementation of the video chat
@login_required
def index(request):
    return render(request, 'video_chat/index.html', {})


@login_required
def videoChat(request, room_token):
    context = {'room_token': room_token,
               }
    return render(request, 'video_chat/video_chat.html', context)

'''
@login_required
def videoChat(request):
    return render(request, 'video_chat/video_chat.html', {})
'''

