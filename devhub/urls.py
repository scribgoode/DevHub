"""
URL configuration for devhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import Profile, myProfile, home, index, videoChat
from accounts import views

urlpatterns = [
    # admin pages
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    #path('', include('accounts.urls')), #moved the home views in accounts to here

    # user pages
    path('my-profile/', myProfile, name='my-profile'),
    path('profile/<int:id>', Profile, name='profile'),
    path('', home, name='home'),

    # api pages
    path('api-auth/', include('rest_framework.urls')),
    path('api/profiles/', views.profile_list),
    path('api/get-profile/<int:pk>', views.profile_detail),
    path('api/rooms/', views.room_list),
    path('api/get-rooms/<int:pk>', views.get_room),
    path('api/messages/', views.message_list),
    path('api/get-chathistory/<uuid:pk>', views.get_chat),
    #path('', include('chat.urls')),

    # video pages
    path('index/', index, name='index'),#this is apart of testing for the implementation of the video chat
    path('my-profile/video_chat/<str:room_token>', videoChat, name='video_chat'),#i need to serialize the room object into json i think leland has already done this do i need to figure how to use the rest framework #actually nope
    #path('my-profile/video_chat/', videoChat, name='video_chat'),
]
