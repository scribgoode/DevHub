from django.db import models
from django.contrib.auth.models import AbstractUser

class Engineer(AbstractUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    class Status(models.TextChoices):
        CREATOR = 'creator', 'creator'
        RECRUIT = 'recruit', 'recruit'

    status = models.CharField(max_length=7, choices=Status.choices, default=Status.RECRUIT)
    current_project = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(null=True)

    class Meta:
        verbose_name_plural = 'Engineers'

    def __str__(self):
        return self.email