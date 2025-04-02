from text_chat.models import Message
from django.db.models import Count

def unread_message_notifications(request):
    if request.user.is_authenticated:
        unread = (
            Message.objects
            .filter(recipient=request.user, is_read=False)
            .values('sender__username', 'sender__id')
            .annotate(unread_count=Count('id'))
        )
        return {'unread_message_notifications': unread}
    return {'unread_message_notifications': []}
from .models import Engineer

def global_data(request):
    if request.user. is_authenticated:

        current_user = Engineer.objects.get(id=request.user.id)
        favorites = current_user.favorites.all()
    else:
        favorites = []
        
    return {'favorites': favorites}
