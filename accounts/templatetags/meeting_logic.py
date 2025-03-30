from django import template
from video_chat.models import Meeting
from accounts.models import Engineer

register = template.Library()

# Get the sender or recipient name based on the current user ID
@register.simple_tag
def get_meet_user(cur_user_id, meeting):
    return meeting.recipient if cur_user_id == meeting.sender.id else meeting.sender

# Check if the current user has submitted a review
@register.simple_tag
def has_reviewed(cur_user_id, meeting):
    return (meeting.review.sender_status == 'reviewed' if cur_user_id == meeting.sender.id 
            else meeting.review.recipient_status == 'reviewed')

@register.filter
def dict_key(d, key):
    """Safely get a dictionary value in Django templates"""
    if isinstance(d, dict):
        return d.get(key, False)  # Returns False if key is missing
    return False  # If d is not a dictionary, return False
