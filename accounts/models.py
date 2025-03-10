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
    # address = models.CharField(max_length=255, blank=True, null=True)
    projects = models.ManyToManyField('Project', blank=True, null=True) 
    dob = models.DateField(default=date.today)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    elevator_pitch = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True) #cant be a one to one field here because two people that live together can have the same address

    def __str__(self):
        return self.first_name

class Project(models.Model):
    pal = models.ForeignKey(Engineer, on_delete=models.CASCADE) #if we end up doing a clean up of the code then rename engineer to pal
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=4000)
    class Visibility(models.TextChoices): #maybe should make active its own switch
        ACTIVE = 'active', 'active'
        PUBLIC = 'public', 'private'
        PRIVATE = 'private', 'private' 
    visibility = models.CharField(max_length=7, choices=Visibility.choices, default=Visibility.ACTIVE)
    #if we end up making it a project management site too, then we need to add a way to add users to a project but we might want to go ahead and add this so we can use the meetup spot algorithm to find a place between three people
    #we might want to end up setting that up as best we can before putting the website up because ETL is an expensive process but maybe not because of scope creep
 