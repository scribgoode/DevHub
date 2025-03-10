from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingRequestViewSet

router = DefaultRouter()
router.register(r'meeting-requests', MeetingRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]