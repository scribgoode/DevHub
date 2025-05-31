from celery import shared_task
from video_chat.models import Meeting

@shared_task
def set_meeting_status(meeting_id, new_status):
    print(f"🔄 Attempting to update Meeting {meeting_id} status to {new_status}")
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        print(f"🔄 Updating Meeting {meeting.id} status from {meeting.status} to {new_status}")
        old_status = meeting.status

        if old_status == Meeting.Status.CANCELLED:
            print(f"⛔ Skipped: Meeting {meeting.id} is already cancelled (currently {old_status})")
            return
        
        if old_status == Meeting.Status.RESCHEDULED:
            print(f"⛔ Skipped: Meeting {meeting.id} is already rescheduled (currently {old_status})")
            return
        
        if old_status == Meeting.Status.COMPLETED:
            print(f"⛔ Skipped: Meeting {meeting.id} is already completed (currently {old_status})")
            return
    
        if old_status == new_status:
            print(f"✅ No change: Meeting {meeting.id} is already in status {old_status}")
            return


        meeting.status = new_status
        meeting._actor = "system"  # Simulate system update
        meeting.save()

        print(f"✅ Meeting {meeting.id} updated from {old_status} to {new_status}")

    except Meeting.DoesNotExist:
        print(f"❌ Meeting {meeting_id} not found")
