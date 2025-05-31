from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

# Signal to activate user's timezone upon login

@receiver(user_logged_in)
def activate_user_timezone(sender, user, request, **kwargs):
    if hasattr(user, 'timezone'):
        timezone.activate(user.timezone)
