from typing import Any

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


@register.filter
def seconds_to_minutes(value):
    try:
        value = int(value)
        minutes = value / 60
        return f"{minutes:.1f}"
    except (TypeError, ValueError):
        return "0"


@register.filter
def filter_exercise_type(exercises, exercise_type):
    """Filter exercises by type"""
    return [
        exercise for exercise in exercises if exercise["exercise_type"] == exercise_type
    ]


@register.filter
def has_exercise_type(exercises, exercise_type):
    """Check if any exercise in the list has the specified type"""
    return any(exercise["exercise_type"] == exercise_type for exercise in exercises)


@register.filter
def group_consecutive_exercises(exercises):
    """Group consecutive exercises of the same type"""
    if not exercises:
        return []

    groups = []
    current_group: list[Any] = []
    current_type = None

    for exercise in exercises:
        exercise_type = exercise["exercise_type"]
        if current_type != exercise_type:
            if current_group:
                groups.append({"type": current_type, "exercises": current_group})
            current_group = [exercise]
            current_type = exercise_type
        else:
            current_group.append(exercise)

    # Add the last group
    if current_group:
        groups.append({"type": current_type, "exercises": current_group})

    return groups


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)
