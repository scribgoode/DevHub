from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Engineer, Project, AGENDA_CHOICES, Interest, Idea
from allauth.account.forms import SignupForm
from django import forms
from cities_light.models import City, Country
from meetup_point.models import Address
from django_flatpickr.widgets import DatePickerInput
from pytz import all_timezones

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Engineer
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):
    agenda = forms.MultipleChoiceField(
        choices=AGENDA_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple  # Or SelectMultiple if you prefer dropdown
    )
    class Meta:
        model = Engineer
        fields = '__all__'


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='first_name')
    last_name = forms.CharField(max_length=30, label='last_name')
    dob = forms.DateField(label='dob', widget=DatePickerInput(attrs={"class": "signup-input-box-widget"}))
    address = forms.CharField(max_length=255, label='address') 
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City", label='city')
    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select Country", label='country')
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in all_timezones], initial='UTC')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.address = Address.objects.create(street=self.cleaned_data['address'])
        user.country = self.cleaned_data['country']
        user.dob = self.cleaned_data['dob']
        user.city = self.cleaned_data['city']
        user.timezone = self.cleaned_data['timezone']
        user.save()
        return user
    
class LocationFilterForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City")
    def __init__(self, *args, **kwargs):
        super(LocationFilterForm, self).__init__(*args, **kwargs)
        self.fields['city'].required = False

class ElevatorPitchForm(forms.ModelForm):
    class Meta:
        model = Engineer
        fields = ['elevator_pitch']

class ProjectCreationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'display_on_profile', 'actively_recruiting', 'contribution_explanation']

class InterestCreationForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['subject', 'interested_in_joining']

class IdeaCreationForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['subject', 'rough_idea']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Engineer
        fields = ['first_name', 'last_name', 'city', 'meeting_preference', 'agenda', 'open_to_contributing',] 
