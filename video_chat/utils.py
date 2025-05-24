from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now
from .models import Notification
from celery.result import AsyncResult
from video_chat.tasks.meeting_tasks import set_meeting_status

from datetime import datetime
from django.utils.timezone import make_aware, is_aware, utc

from django.utils.timezone import localtime
import pytz


def notify_meeting_status_cancelled(meeting_obj, sender, recipient):
    # this is user made
    type_map = {
        "in-person": "in person",
        "video": "online"
    }
    print("obj: ", meeting_obj.type)

    meeting_type = type_map.get(meeting_obj.type, "unknown")
    msg = f"Your meeting with {sender.first_name} has been cancelled.\nReason: {meeting_obj.cancel_reason}"
    
    notification = Notification.objects.create(user=recipient, message=msg)

    # Convert timestamp to recipient's timezone
    user_tz = pytz.timezone(recipient.timezone or 'UTC')
    notification_time = localtime(notification.created_at, timezone=user_tz)

    # Format it for the frontend
    formatted_time = notification_time.isoformat()

    channel_layer = get_channel_layer()
    print("✅ Sending user update for notification", notification.id)
    async_to_sync(channel_layer.group_send)(
        f'user_{recipient.id}',
        {
            'type': 'notification_message',
            'id': notification.id,
            'sender': sender.get_full_name(),
            'message': msg,
            'created_at': formatted_time,
            'notification_type': 'meeting_update',
        }
    )

def notify_meeting_status_change(meeting_obj, old_status, new_status, sender, recipient):
    # This is a system update
    # for every user in the meeting, send a notification
    channel_layer = get_channel_layer()

    for user in meeting_obj.participants():
        # determine meeting type
        type_map = {
            "in-person": "in person",
            "video": "online"
        }
        print("obj: ", meeting_obj.type)
        meeting_type = type_map.get(meeting_obj.type, "unknown")

        # Determine the message based on the status change
        msg_recipient = recipient if user == sender else sender
        status_messages = {
            ("upcoming", "ongoing"): f"Your meeting with {msg_recipient.first_name} {meeting_type} is starting!",
            ("upcoming", "cancelled"): f"Your meeting with {msg_recipient.first_name} has been cancelled.\nReason: {meeting_obj.cancel_reason}", # system cancel meeting is not implemented yet
            ("ongoing", "reviewing"): f"Thank you for completing your meeting with {msg_recipient.first_name}. Please take a moment to review the meeting.",
            ("reviewing", "completed"): f"Thank you for reviewing your meeting with {msg_recipient.first_name}. The meeting is now complete.",
        }
        
        msg = status_messages.get(
            (old_status, new_status),
            f"Your meeting with {msg_recipient.first_name} changed from {old_status} to {new_status}. - THIS IS EDGE CASE, notify admins!"
        )


        notification = Notification.objects.create(user=user, message=msg)

        # Convert timestamp to recipient's timezone
        user_tz = pytz.timezone(user.timezone or 'UTC')
        notification_time = localtime(notification.created_at, timezone=user_tz)

        # Format it for the frontend
        formatted_time = notification_time.isoformat()
        print("formatted_time: ", formatted_time)

        print("✅ Sending annoucement for notification", notification.id, " to user", user.id)
        async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
            {
                'type': 'notification_message',
                'id': notification.id,
                'sender': "System Announcement",
                'message': msg,
                'created_at': formatted_time,
                'notification_type': 'meeting_update',
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

    # Convert timestamp to recipient's timezone
    user_tz = pytz.timezone(recipient.timezone or 'UTC')
    print("user_tz: ", user_tz)
    notification_time = localtime(notification.created_at, timezone=user_tz)
    print("notification_time: ", notification_time)
    # Format it for the frontend
    formatted_time = notification_time.isoformat()
    print("formatted_time: ", formatted_time)

    print("✅ Sending group_send for notification", notification.id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{recipient.id}',
        {
            'type': 'notification_message',
            'id': notification.id,
            'sender': sender.get_full_name(),
            'message': msg,
            'created_at': formatted_time,
            'notification_type': 'request_update',
        }
    )

from django.utils.timezone import is_aware, make_aware, utc

def schedule_meeting_status_updates(meeting):
    if meeting.start_time and meeting.end_time:
        start_datetime = meeting.start_time
        end_datetime = meeting.end_time

        print("start_time:", start_datetime)
        print("tzinfo:", start_datetime.tzinfo)

        # Ensure both datetimes are timezone-aware in UTC
        if not is_aware(start_datetime):
            start_datetime = make_aware(start_datetime)
        if not is_aware(end_datetime):
            end_datetime = make_aware(end_datetime)

        print(f"Scheduling status updates for Meeting {meeting.id} at {start_datetime} and {end_datetime}")

        # Schedule Celery tasks
        ongoing_task = set_meeting_status.apply_async(
            args=[meeting.id, 'ongoing'],
            eta=start_datetime
        )

        reviewing_task = set_meeting_status.apply_async(
            args=[meeting.id, 'reviewing'],
            eta=end_datetime
        )

        # Save task IDs to model
        meeting.ongoing_task_id = ongoing_task.id
        meeting.reviewing_task_id = reviewing_task.id
        meeting.save()

def cancel_meeting_status_tasks(meeting, user=None):
    if meeting.ongoing_task_id:
        AsyncResult(meeting.ongoing_task_id).revoke(terminate=True)
        print(f"🔴 Revoked ongoing task {meeting.ongoing_task_id}")

    if meeting.reviewing_task_id:
        AsyncResult(meeting.reviewing_task_id).revoke(terminate=True)
        print(f"🔴 Revoked reviewing task {meeting.reviewing_task_id}")

    # Clear task IDs
    meeting.ongoing_task_id = None
    meeting.reviewing_task_id = None
    meeting.save()