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
from accounts.views import myProfile, home
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    #path('', include('accounts.urls')), #moved the home views in accounts to here
    path('my_profile/<int:id>', myProfile, name='my_profile'),
    path('', home, name='home'),
    path('api-auth/', include('rest_framework.urls')),
    path('profiles/', views.profile_list),
    path('profiles/<int:pk>', views.profile_detail),
    path('rooms/', views.room_list),
    path('rooms/<int:pk>', views.get_room),
    path('messages/', views.message_list),
    path('messages/<uuid:pk>', views.get_chat),
    #path('', include('chat.urls')),
]
