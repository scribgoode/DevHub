# filepath: /c:/Users/lelan/Documents/projects/DevHub/accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('meetup_point/home.html', views.home, name='home'),
    # Other URL patterns...
]