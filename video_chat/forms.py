from django import forms
from .models import MeetingRequest

class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = MeetingRequest
        fields = [ 'type', 'date', 'start_time', 'end_time', 'message'] 