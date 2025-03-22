from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Engineer, Project

#edit this class to change what the admin page looks like
#field sets is for what the page looks like when you click on it
#do not have to make migrations for this to work
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Engineer

    fieldsets = (
        (None, {'fields': ('email', 'password', 'dob', 'first_name', 'last_name', 'status', 'projects', 'country', 'city', 'elevator_pitch', 'address', 'meeting_preference')}),
    )

    list_display = ["email", "status", "last_login"]

admin.site.register(Engineer, CustomUserAdmin)
admin.site.register(Project)