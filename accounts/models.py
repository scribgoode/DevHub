from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser

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
    current_project = models.TextField(max_length=4000, blank=True, null=True)
    dob = models.DateField(default=date.today)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    # userlist=keylist save to db
    # userList = [test1, test2, test3]

    # model for room
    # roomDic = {(curUser, profileUser): chatHistory}


    def __str__(self):
        return self.first_name
