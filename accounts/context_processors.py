from text_chat.models import Message
from .models import Engineer
from django.db.models import Count

# def unread_message_notifications(request):
#     if request.user.is_authenticated:
#         unread = (
#             Message.objects
#             .filter(recipient=request.user, is_read=False)
#             .values('sender__username', 'sender__id')
#             .annotate(unread_count=Count('id'))
#         )
#         return {'unread_message_notifications': unread}
#     return {'unread_message_notifications': []}


def global_data(request):
    if request.user. is_authenticated:
        
        unread = (
            Message.objects
            .filter(recipient=request.user, is_read=False)
            .values('sender__first_name', 'sender__id')
            .annotate(unread_count=Count('id'))
        )
        unread = list(unread)

        unread_total_count = (
            Message.objects
            .filter(recipient=request.user, is_read=False)
            .count()
        )


        current_user = Engineer.objects.get(id=request.user.id)
        favorites = current_user.favorites.all()
         
        
    else:
        favorites = []
        unread = []
        unread_total_count = 0
        
    return {'favorites': favorites,
            'unread_message_notifications': {
                'unread': unread,
                'unread_total_count': unread_total_count,
    }}
