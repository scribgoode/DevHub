from django.utils import timezone
import pytz

class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"🌀 Middleware triggered for path: {request.path}")

        if request.path.startswith('/admin'):
            timezone.activate(pytz.UTC)
            print("[TimezoneMiddleware] Admin path: forcing UTC")
        elif request.user.is_authenticated:
            user_tz = getattr(request.user, 'timezone', 'UTC')
            try:
                timezone.activate(pytz.timezone(user_tz))
                print(f"[TimezoneMiddleware] Activated timezone: {user_tz}")
            except Exception as e:
                timezone.deactivate()
                print(f"[TimezoneMiddleware] Failed to activate {user_tz}: {e}")
        else:
            timezone.deactivate()
            print("[TimezoneMiddleware] Anonymous user — deactivated timezone")

        return self.get_response(request)
