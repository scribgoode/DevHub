from text_chat.models import Message
from video_chat.models import Notification
from .models import Engineer
from django.db.models import Count

def global_data(request):
    # Default fallback data
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

        # Total unread message count
        unread_msgs_total_count = unread_msgs.aggregate(total=Count('unread_count'))['total'] or 0

        # Unread meeting notifications
        unread_meeting_status = Notification.objects.filter(
            user=request.user, is_read=False
        ).order_by('-created_at')

        # Favorites (gracefully fallback if not an Engineer)
        try:
            current_user = Engineer.objects.get(id=request.user.id)
            favorites = current_user.favorites.all()
        except Engineer.DoesNotExist:
            favorites = []

        # Final context assignment
        context['favorites'] = favorites
        context['unread_notifications']['unread_msgs'] = list(unread_msgs)
        context['unread_notifications']['unread_msgs_total_count'] = unread_msgs_total_count
        context['unread_notifications']['unread_meeting_status'] = unread_meeting_status
        context['unread_notifications']['unread_meeting_status_count'] = unread_meeting_status.count()

    return context
