from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from meetup_point.models import Address
from datetime import timedelta, datetime
from django.contrib.postgres.fields import ArrayField

def video_upload_path(instance, filename):
    return f'videos/{filename}'

def thumbnail_upload_path(instance, filename):
    return f'videos/thumbnails/{filename}'

AGENDA_CHOICES = (
    ('starting', 'Starting Something'),
    ('joining', 'Joining In'),
    ('brainstorming', 'Brainstorming')
)

class Engineer(AbstractUser):
    class Meta:
        verbose_name = 'Engineer'
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    agenda = ArrayField(models.CharField(max_length=100, choices=AGENDA_CHOICES), blank=True, default=list, null=True)
    # address = models.CharField(max_length=255, blank=True, null=True)
    projects = models.ManyToManyField('Project', blank=True) 
    dob = models.DateField(default=date.today)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    timezone = models.CharField(max_length=64, default='UTC')
    
    elevator_pitch = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    elevator_pitch_thumbnail = models.FileField(upload_to=thumbnail_upload_path, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True) #cant be a one to one field here because two people that live together can have the same address
    favorites = models.ManyToManyField('Engineer', symmetrical=False, blank=True) #not working
    online_status = models.BooleanField(default=False)
    
    # Rating system
    rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    reviews = models.ManyToManyField('Review', blank=True, related_name='engineer_review')  # Fixed model name and added related_name

    # Meeting
    NumMeetings = models.IntegerField(default=0)
    NumInPersonMeetings = models.IntegerField(default=0)
    NumVideoMeetings = models.IntegerField(default=0)
    
    class MeetingPreference(models.TextChoices):
        INPERSON = 'in-person', 'in-person'
        VIDEO = 'video', 'video'
        TEXT = 'text', 'text'

    meeting_preference = models.CharField(max_length=9, choices=MeetingPreference.choices, default=MeetingPreference.INPERSON)
    class OpenToContributingDecision(models.TextChoices):
        YES = 'yes', 'yes'
        NO = 'no', 'no'
    open_to_contributing = models.CharField(max_length=3, choices=OpenToContributingDecision.choices, default=OpenToContributingDecision.YES)

    def __str__(self):
        return self.first_name
    
    def last_login_within_7_days(self):
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        # Check if last_login is not None to avoid AttributeError
        if self.last_login is None:
            return False
        # Check if last_login is within the last 7 days
        if self.last_login.date() > seven_days_ago:
            return True
        else:
            return False
    
    def last_login_within_30_days(self):
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        # Check if last_login is not None to avoid AttributeError
        if self.last_login is None:
            return False
        
        if self.last_login.date() > thirty_days_ago:
            return True
        else:
            return False

#create a model and add both foreign keys from project and engineer to create a many to many relationship that we can add more fields to if needed

class Project(models.Model):
    pal = models.ForeignKey(Engineer, on_delete=models.CASCADE,  related_name='project') #if we end up doing a clean up of the code then rename engineer to pal
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=4000)
    class YesandNo(models.TextChoices):
        YES = 'yes', 'yes'
        NO = 'no', 'no'
    display_on_profile = models.CharField(max_length=3, choices=YesandNo.choices, default=YesandNo.YES)
    actively_recruiting  = models.CharField(max_length=3, choices=YesandNo.choices, default=YesandNo.YES, help_text="'Yes also makes the project show up on the home page'")
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    current = models.BooleanField(default=False)
    link = models.URLField(max_length=255, blank=True, null=True)
    contribution_explanation = models.TextField(max_length=15, null=True, blank=True)

    #if we end up making it a project management site too, then we need to add a way to add users to a project but we might want to go ahead and add this so we can use the meetup spot algorithm to find a place between three people
    #we might want to end up setting that up as best we can before putting the website up because ETL is an expensive process but maybe not because of scope creep

class Interest(models.Model):
    pal = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=True, null=True)
    interested_in_joining = models.TextField(max_length=4000, blank=True, null=True)

class Idea(models.Model):
    pal = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=True, null=True)
    rough_idea = models.TextField(max_length=4000, blank=True, null=True)


 # I think there should be a list of reviews for users to see, we should use it internally to see if the reviews are valid for the rating
class Review(models.Model):
    reviewer = models.ForeignKey(
        'accounts.Engineer', on_delete=models.CASCADE, related_name='review_given'
    )
    reviewee = models.ForeignKey(
        'accounts.Engineer', on_delete=models.CASCADE, related_name='review_received'
    )
    meeting = models.ForeignKey(
        'video_chat.Meeting', on_delete=models.CASCADE, related_name='meeting_review'
    )  # Use a string reference for the Meeting model
    review = models.TextField(max_length=1000)
    rating = models.FloatField(default=0)
    meeting_date = models.DateField(default=date.today)
    submitted_date = models.DateField(default=date.today)

    def __str__(self):
        return self.review
    