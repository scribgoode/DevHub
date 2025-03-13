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
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    dob = forms.DateField(label='DOB')
    address = forms.CharField(max_length=255)
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City")
    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select City")

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
        fields = ['title', 'description', 'visibility'] 
