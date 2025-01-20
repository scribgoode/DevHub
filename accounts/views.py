from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Engineer
from text_chat.models import Room, Message

from django.http import JsonResponse
from accounts.serializers import EngineerSerializer, RoomSerializer, MessageSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view

'''
class HomePageView(TemplateView):
    template_name = "home.html"
'''

def home(request):
    profiles = Engineer.objects.all()
    context = {'profiles': profiles,}
    return render(request, 'home.html', context)

def myProfile(request, id):
    profile = Engineer.objects.get(id=id)
    all_profiles = Engineer.objects.all()
    rooms = list(Room.objects.filter(users=profile))
    messages = list(Message.objects.all())
    context = {'profile': profile, 'all_profiles': all_profiles, 'rooms': rooms, 'messages': messages}
    return render(request, 'my_profile.html', context)

@api_view(['GET'])
def profile_list(request):
    print('here')
    profiles = Engineer.objects.all()
    serializer = EngineerSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def profile_detail(request, pk):
    profile = get_object_or_404(Engineer, pk=pk)
    serializer = EngineerSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
def room_list(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_room(request, pk):
    rooms = Room.objects.filter(users__id=pk)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def message_list(request):
    message_list = Message.objects.all()
    serializer = MessageSerializer(message_list, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_chat(request, pk):
    messages = Message.objects.filter(room_id=pk)
    print(messages)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

