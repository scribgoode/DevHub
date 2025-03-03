# filepath: /c:/Users/lelan/Documents/projects/DevHub/accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('meetup_point/home.html', views.home, name='home'),
    path("meetup_point/validate-address", views.validate_address_view, name="validate_address"),
    #path('meetup_point/get-directions', views.get_directions_view, name='get_directions'),
    # Other URL patterns...
]