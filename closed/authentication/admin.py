from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Engineer

class CustomUserAdmin(UserAdmin):
    model = Engineer
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('status', 'current_project', 'address', 'dob')}),
    )
    
    list_display = ["email",]

admin.site.register(Engineer, CustomUserAdmin)
