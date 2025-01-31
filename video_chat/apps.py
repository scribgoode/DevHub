from django.apps import AppConfig


<<<<<<<< HEAD:text_chat/apps.py
class TextChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'text_chat'
========
class VideoChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_chat'
>>>>>>>> video_chat:video_chat/apps.py
