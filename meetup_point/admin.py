from django.contrib import admin
from meetup_point.models import Address

class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', 'country']

admin.site.register(Address, AddressAdmin)