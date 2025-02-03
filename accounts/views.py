from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Engineer
from cities_light.models import City
from text_chat.models import Room, Message
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from accounts.serializers import EngineerSerializer, RoomSerializer, MessageSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
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
    profile = Engineer.objects.get(id=id)
    context = {'profile': profile}
    return render(request, 'profile.html', context)

def myProfile(request):
    return render(request, 'my_profile.html')

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admin users can access this view
def profile_list(request):
    print('here')
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

