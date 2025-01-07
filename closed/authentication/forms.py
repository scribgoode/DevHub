from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Engineer

class CustomUserCreationForm(UserCreationForm):
    username = None
    class Meta:
        model = Engineer
        fields = ('email', 'first_name', 'last_name', 'status', 'current_project', 'address', 'dob')

class CustomUserChangeForm(UserChangeForm):
    username = None
    class Meta:
        model = Engineer
        fields = ['email', 'first_name', 'last_name', 'status', 'current_project', 'address', 'dob']