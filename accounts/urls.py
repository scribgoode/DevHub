# filepath: /c:/Users/lelan/Documents/projects/DevHub/accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile_json/<int:id>/', views.profile_json, name='profile_json'),
    # Other URL patterns...
]