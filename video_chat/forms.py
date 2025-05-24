from django import forms
from django_flatpickr.widgets import DatePickerInput, TimePickerInput
from .models import MeetingRequest
from datetime import datetime
from django.utils.timezone import make_aware
import pytz

class MeetingRequestForm(forms.ModelForm):
    # These are form-only fields
    date = forms.DateField(widget=DatePickerInput())
    start_time = forms.TimeField(
        widget=TimePickerInput(),
        input_formats=[
            "%H:%M:%S",   # e.g., 12:00:00
            "%H:%M",      # e.g., 12:00
            "%I:%M %p",   # e.g., 12:00 PM
            "%I:%M %P",   # e.g., 12:00 pm
        ]
    )

    end_time = forms.TimeField(
        widget=TimePickerInput(),
        input_formats=[
            "%H:%M:%S",
            "%H:%M",
            "%I:%M %p",
            "%I:%M %P",
        ]
    )


    class Meta:
        model = MeetingRequest
        fields = ['type', 'message']  # model has start_time, but it's not shown here

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        print("Saving MeetingRequestForm")
        instance = super().save(commit=False)

        # Combine date and time into a datetime
        date = self.cleaned_data['date']
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        print(f"Date: {date}, Start Time: {start_time}, End Time: {end_time}")
        user_tz = pytz.timezone(self.user.timezone)
        start_time_datetime = make_aware(datetime.combine(date, start_time), user_tz)
        end_time_datetime = make_aware(datetime.combine(date, end_time), user_tz)
        print(f"Start Time Datetime: {start_time_datetime}, End Time Datetime: {end_time_datetime}")
        # Store it in the model's DateTimeField
        instance.start_time = start_time_datetime
        instance.end_time = end_time_datetime
        instance.date = start_time_datetime.date()  # Store the date separately if needed

        if commit:
            instance.save()

        return instance
