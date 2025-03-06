from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from meetup_point.models import Address

def video_upload_path(instance, filename):
    return f'videos/{filename}'

class Engineer(AbstractUser):
    class Meta:
        verbose_name = 'Engineer'
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    class Status(models.TextChoices):
        CREATOR = 'creator', 'creator'
        RECRUIT = 'recruit', 'recruit'

    status = models.CharField(max_length=7, choices=Status.choices, default=Status.RECRUIT)
    current_project = models.CharField(max_length=200, blank=True, null=True)
    # address = models.CharField(max_length=255, blank=True, null=True)
    current_project = models.TextField(max_length=4000, blank=True, null=True)
    dob = models.DateField(default=date.today)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    elevator_pitch = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return self.first_name
