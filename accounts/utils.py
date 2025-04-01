# utils.py or views.py

from django.db.models import Count, Q
from text_chat.models import Message

def get_unread_message_counts(user):
    # Count unread messages per sender
    return Message.objects.filter(
        recipient=user,
        is_read=False
    ).values('sender').annotate(unread=Count('id'))
