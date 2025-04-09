from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Engineer, Project
from allauth.account.forms import SignupForm
from django import forms
from cities_light.models import City, Country
from meetup_point.models import Address

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Engineer
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Engineer
        fields = ("username", "email")


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='first_name')
    last_name = forms.CharField(max_length=30, label='last_name')
    dob = forms.DateField(label='dob')
    address = forms.CharField(max_length=255, label='address')
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City", label='city')
    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select Country", label='country')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.address = Address.objects.create(street=self.cleaned_data['address'])
        user.country = self.cleaned_data['country']
        user.dob = self.cleaned_data['dob']
        user.city = self.cleaned_data['city']
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

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Engineer
        fields = ['first_name', 'last_name', 'city', 'meeting_preference', 'status', 'open_to_contributing',] 
