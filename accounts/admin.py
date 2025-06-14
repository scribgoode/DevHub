from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Engineer, Project, Review, Interest, Idea

#edit this class to change what the admin page looks like
#field sets is for what the page looks like when you click on it
#do not have to make migrations for this to work
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Engineer

    fieldsets = (
        (None, {'fields': ('email', 'password', 'timezone', 'dob', 'first_name', 'last_name', 'online_status_visible', 'online_status', 'agenda', 'projects', 'country', 'city', 'elevator_pitch', 'elevator_pitch_thumbnail', 'address', 'favorites', 'meeting_preference', 'rating', 'rating_count', 'NumMeetings', 'NumInPersonMeetings', 'NumVideoMeetings')}),
    )

    list_display = ["email", "agenda", "last_login"]

admin.site.register(Engineer, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(Review)
admin.site.register(Interest)
admin.site.register(Idea) 