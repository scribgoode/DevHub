from django.urls import reverse
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from .models import Engineer, Project
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
from accounts.forms import ProjectCreationForm
import requests
from django.db.models import Case, When

'''
class HomePageView(TemplateView):
    template_name = "home.html"
'''

def signUp(request):
    return render(request, 'accounts/signup.html')

def login(request): 
    return render(request, 'accounts/login.html')  

def home(request):
    profiles = Engineer.objects.all()
    pitch = request.GET.get('pitch')
    preference = request.GET.get('preference')
    status = request.GET.get('status')
    city = request.GET.get('city') 
    search = request.GET.get('search') 

    if 'search' in request.GET:
        profiles = profiles.filter(Q(first_name__icontains=search) | Q(projects__description__icontains=search))

    if 'city' in request.GET:
        if city != 'any':
            profiles = profiles.filter(city__name=city)

    if 'status' in request.GET:
        #status = request.GET['status'] 
        if status != 'any':
            profiles = profiles.filter(status=status)

    if 'preference' in request.GET:
        #preference = request.GET['preference']
        if preference != 'any':
            profiles = profiles.filter(meeting_preference=preference)
            
    if 'pitch' in request.GET:
        #pitch = request.GET['pitch']
        if pitch == 'true':
            profiles = profiles.filter(elevator_pitch__isnull=False).exclude(elevator_pitch='')
        if pitch == 'false':
            profiles = profiles.filter(Q(elevator_pitch=True) | Q(elevator_pitch=''))
    
    cities = City.objects.all()
    context = {'profiles': profiles,
               'cities': cities,
               'status': status,
               'preference': preference,
               'pitch': pitch,
               'city': city,
               'search': search} 
    
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
            if meeting_request.type == 'in-person':
                # check if both users have addresses
                if request.user.address is not None and Engineer.objects.get(id=id).address is not None:
                    # Convert address objects to JSON-serializable format
                    address_one = {
                        'street': request.user.address.street,
                        'city': {
                            'id': request.user.address.city.id,
                            'name': request.user.address.city.name,
                            'country': {
                                'id': request.user.address.city.country.id,
                                'name': request.user.address.city.country.name
                            }
                        },
                        'state': request.user.address.state,
                        'zip_code': request.user.address.zip_code,
                        'country': {
                            'id': request.user.address.country.id,
                            'name': request.user.address.country.name
                        }
                    }
                    address_two = {
                        'street': Engineer.objects.get(id=id).address.street,
                        'city': {
                            'id': Engineer.objects.get(id=id).address.city.id,
                            'name': Engineer.objects.get(id=id).address.city.name,
                            'country': {
                                'id': Engineer.objects.get(id=id).address.city.country.id,
                                'name': Engineer.objects.get(id=id).address.city.country.name
                            }
                        },
                        'state': Engineer.objects.get(id=id).address.state,
                        'zip_code': Engineer.objects.get(id=id).address.zip_code,
                        'country': {
                            'id': Engineer.objects.get(id=id).address.country.id,
                            'name': Engineer.objects.get(id=id).address.country.name
                        }
                    }

                    # Generate the URL for the find_halfway view
                    find_halfway_url = request.build_absolute_uri(reverse('find_halfway_view'))
                    # Send a POST request to the find_halfway view
                    print('before posting')
                    response = requests.post(
                        find_halfway_url,
                        json={
                            'addressOne': address_one,
                            'addressTwo': address_two
                        }
                    )
                    print('after posting')
                    if response.status_code == 200:
                        data = response.json()
                        redirect_url = f"{data['redirect_url']}?sender={request.user.id}&recipient={Engineer.objects.get(id=id).id}"
                        print('redirect_url:', redirect_url)
                        meeting_request.locationUpdateURL = redirect_url
                        meeting_request.save()
                        return redirect(redirect_url)
                    else:
                        messages.error(request, 'Failed to find halfway point.')
                else:
                    messages.warning(request, 'Both users must have an address to request an in-person meeting.')
            elif meeting_request.type == 'video':
                meeting_request.status = 'pending'
                meeting_request.save()
                return redirect('profile', id=request.user.id)  # Redirect to the profile page after form submission
            else:
                messages.warning(request, 'Meeting request created successfully, but failed to find half way point. THIS SHOULD NOT HAVE HAPPENED!')
                return redirect('profile', id=id)  # Redirect to the profile page after form submission
    else:
        meeting_request_form = MeetingRequestForm()

    profile = Engineer.objects.get(id=id)
    projects = Project.objects.filter(pal__id=id)
    context = {'profile': profile,
               'form': meeting_request_form,
               'projects': projects}
    return render(request, 'profile.html', context)

def myProfile(request):
    print(request.POST)
    if request.method == 'POST':
        form_type = request.POST.get("form_type")
        print(form_type)
        if form_type ==  "meeting_request_decision":
            meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
            if request.POST.get('decision') == 'accept':
                #meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request)
                meeting.save()
                meeting_request.acknowledgement = MeetingRequest.Acknowledgement.RESOLVED
                meeting_request.status = MeetingRequest.Status.ACCEPTED
                meeting_request.save()
            elif request.POST.get('decision') == 'decline':
                #meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('meeting_request_sender_id'), recipient__id=request.POST.get('meeting_request_recipient_id'), status='pending')
                meeting_request.status = MeetingRequest.Status.DECLINED
                meeting_request.save()
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request, status=Meeting.Status.DECLINED)
                meeting.save()
            elif request.POST.get('decision') == 'reschedule':
                meeting_request.status = MeetingRequest.Status.RESCHEDULED
                meeting_request.save()
                meeting = Meeting(sender=meeting_request.sender, recipient=meeting_request.recipient, start_time=meeting_request.start_time, end_time=meeting_request.end_time, date=meeting_request.date, description=meeting_request.message, type=meeting_request.type, meeting_request = meeting_request, status=Meeting.Status.DECLINED)
                meeting.save()
                return redirect('profile', id=request.POST.get('meeting_request_sender_id'))
        if form_type == "video_upload":
            user = request.user
            user.elevator_pitch = request.FILES['elevator_pitch']
            user.save()
        if form_type == "video_remove":
            user = request.user
            user.elevator_pitch.delete()
        if form_type == "add_project":
            form = ProjectCreationForm(request.POST)
            if form.is_valid:
                project = form.save(commit=False)
                project.pal = request.user
                project.save()
       
       # acknowledgement accepted
        if form_type == 'sent-meeting-acknowledgement':
            print('acknowledgement')
            meeting_request = MeetingRequest.objects.get(sender__id=request.POST.get('sent_meeting_sender_id'), recipient__id=request.POST.get('sent_meeting_recipient_id'), status=request.POST.get('send_meeting_status'),acknowledgement='pending')
            if request.POST.get('acknowledgement') == 'acknowledge':
                meeting_request.acknowledgement = MeetingRequest.Acknowledgement.RESOLVED
                meeting_request.save()
                # return redirect('/my_profile')


    meetings = Meeting.objects.filter( Q(recipient=request.user) | Q(sender=request.user) )
    
    # debug - to remove
    for meeting in meetings:
        for field in meeting._meta.fields:
            print(field.name, getattr(meeting, field.name))
    
    meeting_requests = MeetingRequest.objects.filter( Q(recipient=request.user) | Q(sender=request.user) ) #maybe make meeting_requests and sent_meetings_requests
    meeting_requests = meeting_requests.order_by('date', 'start_time')
    
    sent_meetings = MeetingRequest.objects.filter(sender=request.user)
    sent_meetings = sent_meetings.annotate(
        status_order=Case(
            When(status='pending', then=1),
            When(status='accepted', then=2),
            When(status='rescheduled', then=3),
            When(status='declined', then=4),
            default=5
        )
    ).order_by('status_order')
    projects = Project.objects.filter(pal=request.user)
    project_creation_form = ProjectCreationForm()

    context = {'meetings': meetings,
               'meeting_requests': meeting_requests,
               'sent_meetings': sent_meetings,
               'projects': projects,
               'project_creation_form': project_creation_form}

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

