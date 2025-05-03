from django.contrib import admin
from .models import Meeting, MeetingRequest, MeetingReview, Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('message', 'user__username')

admin.site.register(Meeting)
admin.site.register(MeetingRequest)
admin.site.register(MeetingReview)
