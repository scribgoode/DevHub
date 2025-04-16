from django import forms
from .models import MeetingRequest
from django_flatpickr.widgets import DatePickerInput, TimePickerInput

class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = MeetingRequest
        fields = [ 'type', 'date', 'start_time', 'end_time', 'message'] 
        widgets = {
            'date': DatePickerInput(),
            'start_time': TimePickerInput(),
            'end_time': TimePickerInput(range_from='start_time',),
        }
        #add optional project to choose from in meeting request form(get to chose from list of each others projects)