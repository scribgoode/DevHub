from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now
from .models import Notification

def notify_meeting_status_change(meeting, old_status, new_status, recipient):
    msg = f"Meeting '{meeting.title}' changed from {old_status} to {new_status}."

    Notification.objects.create(user=recipient, message=msg)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{recipient.id}',
        {
            'type': 'notification_message',
            'message': msg,
            'created_at': now().isoformat(),
        }
    )

def notify_meeting_request_status_change(request_obj, old_status, new_status, sender, recipient):
    # Determine the message based on the status change

    # sender is the person that acted on the request
    # recipient is the person that received the request notification

    type_map = {
        "in-person": "in person",
        "video": "online"
    }
    print("obj: ", request_obj.type)
    meeting_type = type_map.get(request_obj.type, "unknown")

    status_messages = {
        ("creating", "pending"): f"{sender.first_name} has sent you a Meeting Request to meet {meeting_type}.",
        ("pending", "accepted"): f"{sender.first_name} has accepted the Meeting Request to meet {meeting_type}.",
        ("pending", "declined"): f"{sender.first_name} has declined the Meeting Request to meet {meeting_type}.",
        ("pending", "rescheduled"): f"{sender.first_name} will reschedule the Meeting Request to meet {meeting_type}.",
        ("pending", "cancelled"): f"{sender.first_name} has cancelled the Meeting Request to meet {meeting_type}.",
    }

    msg = status_messages.get(
        (old_status, new_status),
        f"Meeting request from {sender.first_name} changed from {old_status} to {new_status}. - THIS IS EDGE CASE, notify admins!"
    )

    print("recipient: ", recipient)
    print("msg: ", msg)

    notification = Notification.objects.create(user=recipient, message=msg)

    print("✅ Sending group_send for notification", notification.id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{recipient.id}',
        {
            'type': 'notification_message',
            'id': notification.id,
            'sender': sender.get_full_name(),
            'message': msg,
            'created_at': now().isoformat(),
            'notification_type': 'request',
        }
    )