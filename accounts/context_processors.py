from text_chat.models import Message
from video_chat.models import Notification
from .models import Engineer
from django.db.models import Count
from django.utils.timezone import localtime
import pytz

def global_data(request):
    print("global_data context processor")
    context = {
        'favorites': [],
        'unread_notifications': {
            'unread_msgs': [],
            'unread_msgs_total_count': 0,
            'unread_meeting_status': [],
            'unread_meeting_status_count': 0,
        }
    }

    if request.user.is_authenticated:
        # Unread messages grouped by sender
        unread_msgs = (
            Message.objects
            .filter(recipient=request.user, is_read=False)
            .values('sender__first_name', 'sender__id')
            .annotate(unread_count=Count('id'))
        )
        unread_msgs_total_count = sum(msg['unread_count'] for msg in unread_msgs)
        print("user: ", request.user)
        print("user timezone: ", getattr(request.user, 'timezone', 'UTC'))

        # Timezone-aware unread meeting notifications
        user_tz = pytz.timezone(getattr(request.user, 'timezone', 'UTC'))
        notification = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at').first()
        
        unread_meeting_status = [
            {
                'id': n.id,
                'message': n.message,
                'created_at': localtime(n.created_at, timezone=user_tz),
                'is_read': n.is_read,
            }
            for n in Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        ]

        # Favorites
        try:
            current_user = Engineer.objects.get(id=request.user.id)
            favorites = current_user.favorites.all()
        except Engineer.DoesNotExist:
            favorites = []

        # Final context
        context['favorites'] = favorites
        context['unread_notifications']['unread_msgs'] = list(unread_msgs)
        context['unread_notifications']['unread_msgs_total_count'] = unread_msgs_total_count
        context['unread_notifications']['unread_meeting_status'] = unread_meeting_status
        context['unread_notifications']['unread_meeting_status_count'] = len(unread_meeting_status)
        context['user_timezone'] = getattr(request.user, 'timezone', 'UTC')

    return context
