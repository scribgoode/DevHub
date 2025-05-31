from datetime import date, datetime
from time import mktime
from django.db import models
from tzlocal import get_localzone
from accounts.models import Engineer
from text_chat.models import Room
from meetup_point.models import Address
import string
import random
from django.utils.timezone import now, activate, localtime
from django.utils import timezone



# Create your models here.

def generate_random_token(length=20):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Track acknowledgement status for sender and recipient independently
class MeetingReview(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'pending'
        REVIEWED = 'reviewed', 'reviewed'
    
    # Track if both users have submitted their reviews
    review_status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )

    # Track review status for sender
    sender_status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    sender_review = models.TextField(null=True, blank=True)
    sender_rating = models.FloatField(null=True, blank=True)

    # Track review status for recipient
    recipient_status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    recipient_review = models.TextField(null=True, blank=True)
    recipient_rating = models.FloatField(null=True, blank=True)

    # Track the meeting associated with the review
    meeting_date = models.DateField(default=date.today)
    submitted_date = models.DateField(default=date.today)


    def has_reviewed(self, user_id, role):
        if role == 'sender':
            return self.sender_status == self.Status.REVIEWED
        elif role == 'recipient':
            return self.recipient_status == self.Status.REVIEWED
        return False
        
    def __str__(self):
        return f"Sender: {self.sender_status}, Recipient: {self.recipient_status}"

class Meeting(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='recipient')
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_time_unix = models.BigIntegerField(null=True, blank=True)
    end_time_unix = models.BigIntegerField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Track REVIEW status for sender and recipient independently
    review = models.OneToOneField(
        'video_chat.MeetingReview',  # Use a string reference to avoid circular imports
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='meeting_review'
    )
     
    # Track if sender acknowledged the request (reschedule, declined, cancel)
    acknowledged = models.BooleanField(default=False)

    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'upcoming'
        ONGOING = 'ongoing', 'ongoing'
        COMPLETED = 'completed', 'completed'
        REVIEWING = 'reviewing', 'reviewing'
        RESCHEDULED = 'rescheduled', 'rescheduled' # Creates meeting object to reschedule so we can keep track of all meetings
        CANCELLED = 'cancelled', 'cancelled'
        DECLINED = 'declined', 'declined'

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.UPCOMING)

    class Type(models.TextChoices):
        INPERSON = 'in-person', 'in-person'
        VIDEO = 'video', 'video'
        TEXT = 'text', 'text'

    type = models.CharField(max_length=50, choices=Type.choices, default=Type.INPERSON)
    room_token = models.CharField(max_length=255, default=generate_random_token(20))
    meeting_request = models.ForeignKey(
        'MeetingRequest', on_delete=models.CASCADE, related_name='meeting_request', null=True, blank=True
    )

    # celery task ID for meeting status updates
    ongoing_task_id = models.CharField(max_length=255, null=True, blank=True)
    reviewing_task_id = models.CharField(max_length=255, null=True, blank=True)

    def participants(self):
        return [self.sender, self.recipient]

    def save(self, *args, **kwargs):
        print("In save method of Meeting")
        if self.pk:
            print("Meeting with pk exists")
            old = Meeting.objects.get(pk=self.pk)
            if old.status != self.status:
                actor = getattr(self, "_actor", None)  # user who triggered the change
                print(f"Actor: {actor}")
                if actor:
                    if actor != "system":
                        # Notify sender and recipient if the change is made by a user
                        recipient = self.recipient if actor == self.sender else self.sender
                        from .utils import notify_meeting_status_cancelled
                        notify_meeting_status_cancelled(self, actor, recipient)
                    else:
                        # Notify both sender and recipient if the change is made by the system
                        from .utils import notify_meeting_status_change
                        notify_meeting_status_change(self, old.status, self.status, self.sender, self.recipient)

        super().save(*args, **kwargs)

    cancel_reason = models.TextField(null=True, blank=True)
    cancel_user = models.ForeignKey(
        Engineer, on_delete=models.CASCADE, related_name='cancel_user', null=True, blank=True
    )
    
    def can_cancel(self):
        # Check if the meeting is in the future
        if self.status != self.Status.UPCOMING:
            return False
        # Check if the meeting is in the past
        if self.start_time_unix < int(mktime(localtime(now()).timetuple())):
            return False
        
        # Activate the system's timezone
        system_timezone = get_localzone()
        activate(system_timezone)
        # Get the current time in the local timezone
        current_time_unix = int(mktime(now().timetuple()))
        # Check if the meeting can be canceled at least 24 hours before the start time
        return self.start_time_unix - current_time_unix >= 24 * 60 * 60
    
#we need to be sure but we may only need a meeting model for meetings and meeting requests as long as we have enough switches
class MeetingRequest(models.Model):
    sender = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_sender')
    recipient = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='request_recipient')
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    
    
    class Status(models.TextChoices):
        CREATING = 'creating', 'creating'  # creating status
        PENDING = 'pending', 'pending'  # pending status
        ACCEPTED = 'accepted', 'accepted'  # accepted status
        DECLINED = 'declined', 'declined'  # declined status
        RESCHEDULED = 'rescheduled', 'rescheduled'  # rescheduling by recipient
        CANCELLED = 'cancelled', 'cancelled'  # cancelled status by sender

    status = models.CharField(max_length=50, default=Status.CREATING, choices=Status.choices)
    location_name = models.CharField(max_length=255, default='')  # store name (only applicable for in-person meetings)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, default='', null=True, blank=True)  # either URL or address string
    locationUpdateURL = models.CharField(max_length=255, default='', null=True, blank=True)

    class Type(models.TextChoices):
        INPERSON = 'in-person', 'in-person'
        VIDEO = 'video', 'video'
        TEXT = 'text', 'text'

    type = models.CharField(max_length=50, choices=Type.choices, default=Type.INPERSON)

    def save(self, *args, **kwargs):
        print("In save method of MeetingRequest")
        if self.pk:
            print("MeetingRequest with pk exists")
            old = MeetingRequest.objects.get(pk=self.pk)
            if old.status != self.status:
                actor = getattr(self, "_actor", None)  # user who triggered the change
                print(f"Actor: {actor}")
                if actor:
                    recipient = self.recipient if actor == self.sender else self.sender
                    
                    from .utils import notify_meeting_request_status_change
                    notify_meeting_request_status_change(self, old.status, self.status, actor, recipient)
        super().save(*args, **kwargs)


# Notification model for sending notifications to users
class Notification(models.Model):
    user = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
