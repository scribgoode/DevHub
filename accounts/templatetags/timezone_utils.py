from django import template
from django.utils.timezone import localtime
import pytz

register = template.Library()

@register.filter
def to_timezone(value, tz_str):
    try:
        tz = pytz.timezone(tz_str)
        return localtime(value, tz)
    except Exception:
        return value  # Fallback to original
