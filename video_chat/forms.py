from django import forms
from .models import MeetingRequest

class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = MeetingRequest
        fields = [ 'type', 'date', 'start_time', 'end_time', 'message'] 
        #add optional project to choose from in meeting request form(get to chose from list of each others projects)