from django import template

register = template.Library()

@register.filter
def hours_minutes(value):
    try:
        value = int(value)
        hours = value // 60
        minutes = value % 60

        if hours == 0:
            return f"{minutes} min"
        return f"{hours}h{minutes}"
    except (TypeError, ValueError):
        return "Invalid duration"
