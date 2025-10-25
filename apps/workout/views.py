import logging
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Union

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import translation
from django.utils.translation import gettext

from .models import (
    CardioExerciseLog,
    Equipment,
    Exercice,
    MuscleGroup,
    OneExercice,
    StrengthExerciseLog,
    TypeWorkout,
    Workout,
)

logger = logging.getLogger(__name__)


def redirect_workout(request):
    lang = translation.get_language()

    # Get filter parameters
    workout_type_filter = request.GET.get("workout_type", "")
    exercise_filter = request.GET.get("exercise", "")

    # Base queryset
    workouts = Workout.objects.all().order_by("-date")

    # Apply workout type filter (exact match)
    if workout_type_filter:
        workouts = workouts.filter(
            type_workout__name_workout__exact=workout_type_filter
        )

    # Apply exercise filter (filter workouts that contain the specified exercise)
    if exercise_filter:
        workouts = workouts.filter(
            oneexercice__name__name__icontains=exercise_filter
        ).distinct()

    paginator = Paginator(workouts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    workout_data = []
    for workout in page_obj:
        exercises = OneExercice.objects.filter(seance=workout).order_by("position")
        type_workout = (
            workout.type_workout.name_workout if workout.type_workout else "No Type"
        )
        workout_data.append(
            {
                "workout": {
                    "id": workout.id,
                    "date": workout.date.strftime("%-d/%m/%Y"),
                    "type_workout": type_workout,
                    "duration": workout.duration,
                },
                "exercises": [
                    {
                        "id": exercise.id,
                        "name": exercise.name.name if exercise else None,
                        "exercise_type": exercise.name.exercise_type,
                        "data": exercise.get_display_data(),
                        "muscle_groups": list(
                            exercise.name.muscle_groups.all().values_list(
                                "name", flat=True
                            )
                        ),
                    }
                    for exercise in exercises
                ],
            }
        )

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    # Get unique workout types and exercises for filter dropdowns
    all_workout_types = (
        TypeWorkout.objects.all()
        .values_list("name_workout", flat=True)
        .distinct()
        .order_by("name_workout")
    )
    all_exercises = (
        Exercice.objects.all()
        .values_list("name", flat=True)
        .distinct()
        .order_by("name")
    )

    if is_ajax:
        data = {
            "workout_data": workout_data,
            "has_next": page_obj.has_next(),
            "next_page_number": (
                page_obj.next_page_number() if page_obj.has_next() else None
            ),
        }
        return JsonResponse(data)

    context = {
        "page": "workout",
        "lang": lang,
        "workout_data": workout_data,
        "has_next": page_obj.has_next(),
        "next_page_number": (
            page_obj.next_page_number() if page_obj.has_next() else None
        ),
        "workout_type_filter": workout_type_filter,
        "exercise_filter": exercise_filter,
        "all_workout_types": all_workout_types,
        "all_exercises": all_exercises,
        "translations": {
            "exercise": gettext("Exercise"),
            "exercice": gettext("Exercise"),
            "series": gettext("Series"),
            "reps": gettext("Reps"),
            "weight_kg": gettext("Weight (kg)"),
            "duration_min": gettext("Duration (min)"),
            "distance_m": gettext("Distance (m)"),
            "edit": gettext("Edit"),
        },
    }
    return render(request, "workout.html", context)


@login_required
def add_workout(request):
    lang = translation.get_language()

    if request.method == "POST":
        try:
            with transaction.atomic():
                date = request.POST["date"]
                type_workout = request.POST["type_workout"]
                duration = request.POST["duration"]

                type_obj, _ = TypeWorkout.objects.get_or_create(
                    name_workout=type_workout
                )

                workout = Workout.objects.create(
                    date=date, type_workout=type_obj, duration=duration
                )

                # Process exercises in order to avoid duplicates
                exercise_data = {}
                for key, value in request.POST.items():
                    if key.startswith("exercise_") and key.endswith("_name"):
                        exercise_id = key.split("_")[1]
                        if exercise_id not in exercise_data:
                            exercise_data[exercise_id] = {"name": value}
                    elif key.startswith("exercise_") and not key.endswith("_name"):
                        parts = key.split("_")
                        if len(parts) >= 3:
                            exercise_id = parts[1]
                            field_name = "_".join(parts[2:])
                            if exercise_id not in exercise_data:
                                exercise_data[exercise_id] = {}
                            exercise_data[exercise_id][field_name] = value

                # Create exercise logs for each unique exercise
                logger.info(
                    f"Processing {len(exercise_data)} exercises "
                    f"for workout {workout.id}"
                )

                # Sort exercises by their ID to maintain order
                sorted_exercises = sorted(
                    exercise_data.items(), key=lambda x: int(x[0])
                )

                for position, (exercise_id, data) in enumerate(
                    sorted_exercises, start=1
                ):
                    logger.info(
                        f"Processing exercise_id: {exercise_id}, "
                        f"data: {data}, position: {position}"
                    )

                    if "name" not in data:
                        logger.warning(f"Exercise {exercise_id} missing name, skipping")
                        continue

                    try:
                        exercise_obj = Exercice.objects.get(name=data["name"])
                        logger.info(
                            f"Found exercise: {exercise_obj.name} "
                            f"(type: {exercise_obj.exercise_type})"
                        )
                    except Exercice.DoesNotExist:
                        logger.warning(
                            f"Exercise '{data['name']}' not found in database, "
                            f"skipping"
                        )
                        continue

                    # Create specific exercise log based on type
                    exercise_log: Union[StrengthExerciseLog, CardioExerciseLog]
                    if exercise_obj.exercise_type == "strength":
                        logger.info(
                            f"Creating StrengthExerciseLog for "
                            f"exercise: {exercise_obj.name}, workout: {workout.id}"
                        )
                        # Handle empty fields - convert empty string to default values
                        weight = data.get("weight", 0)
                        if weight == "" or weight is None:
                            weight = 0
                        else:
                            weight = int(weight)

                        nb_series = data.get("nb_series", 1)
                        if nb_series == "" or nb_series is None:
                            nb_series = 1
                        else:
                            nb_series = int(nb_series)

                        nb_repetition = data.get("nb_repetition", 1)
                        if nb_repetition == "" or nb_repetition is None:
                            nb_repetition = 1
                        else:
                            nb_repetition = int(nb_repetition)

                        (
                            exercise_log,
                            created,
                        ) = StrengthExerciseLog.objects.get_or_create(
                            exercise=exercise_obj,
                            workout=workout,
                            defaults={
                                "nb_series": nb_series,
                                "nb_repetition": nb_repetition,
                                "weight": weight,
                            },
                        )
                        logger.info(
                            f"StrengthExerciseLog "
                            f"{'created' if created else 'retrieved'}: "
                            f"{exercise_log.id}"
                        )
                        content_type = ContentType.objects.get_for_model(
                            StrengthExerciseLog
                        )

                    elif exercise_obj.exercise_type == "cardio":
                        logger.info(
                            f"Creating CardioExerciseLog for "
                            f"exercise: {exercise_obj.name}, workout: {workout.id}"
                        )
                        exercise_log, created = CardioExerciseLog.objects.get_or_create(
                            exercise=exercise_obj,
                            workout=workout,
                            defaults={
                                "duration_seconds": data.get("duration_seconds"),
                                "distance_m": data.get("distance_m"),
                            },
                        )
                        logger.info(
                            f"CardioExerciseLog "
                            f"{'created' if created else 'retrieved'}: "
                            f"{exercise_log.id}"
                        )
                        content_type = ContentType.objects.get_for_model(
                            CardioExerciseLog
                        )

                    # Create the polymorphic OneExercice entry only if it doesn't exist
                    logger.info(
                        f"Creating OneExercice entry for "
                        f"exercise: {exercise_obj.name} at position {position}"
                    )
                    one_exercice, created = OneExercice.objects.get_or_create(
                        name=exercise_obj,
                        seance=workout,
                        position=position,
                        defaults={
                            "content_type": content_type,
                            "object_id": exercise_log.id,
                        },
                    )
                    logger.info(
                        f"OneExercice {'created' if created else 'retrieved'}: "
                        f"{one_exercice.id}"
                    )

        except Exception as e:
            # If there's any error, redirect back to form with error handling
            logger.error(f"Error creating workout: {str(e)}", exc_info=True)
            return redirect("/workout/add_workout/")

        return redirect("/workout/")

    context = {
        "page": "add_workout",
        "lang": lang,
        "translations": {
            "sets": gettext("Sets"),
            "series": gettext("Series"),
            "reps": gettext("Reps"),
            "repetitions": gettext("Repetitions"),
            "weight_kg": gettext("Weight (kg)"),
            "duration_sec": gettext("Duration (sec)"),
            "distance_m": gettext("Distance (m)"),
        },
    }
    return render(request, "add_workout.html", context)


@login_required
def get_last_workout(request):
    workout_type = request.GET.get("type")
    workout_type_id = TypeWorkout.objects.filter(name_workout=workout_type).first()
    last_workout = (
        Workout.objects.filter(type_workout=workout_type_id).order_by("-date").first()
    )

    all_exercises = (
        Exercice.objects.all().order_by("name").values("name", "exercise_type")
    )

    if last_workout:
        exercises = OneExercice.objects.filter(seance=last_workout).order_by("position")
        exercises_data = []
        for exercise in exercises:
            exercise_data = {
                "name": exercise.name.name,
                "exercise_type": exercise.name.exercise_type,
            }
            exercise_data.update(exercise.get_display_data())
            exercises_data.append(exercise_data)

        data = {
            "date": last_workout.date.strftime("%Y-%m-%d"),
            "exercises": exercises_data,
            "all_exercises": list(all_exercises),
        }
    else:
        data = {"all_exercises": list(all_exercises)}

    return JsonResponse(data)


@login_required
def get_list_exercise(request):
    all_exercises = (
        Exercice.objects.all().order_by("name").values("name", "exercise_type")
    )
    data = {"all_exercises": list(all_exercises)}
    return JsonResponse(data)


@login_required
def get_workout_types(request):
    workout_types = TypeWorkout.objects.all().order_by("name_workout")

    workout_types_data = []
    for workout_type in workout_types:
        workout_types_data.append(
            {"value": workout_type.name_workout, "display": workout_type.name_workout}
        )

    data = {"workout_types": workout_types_data}
    return JsonResponse(data)


@login_required
def edit_workout(request, workout_id):
    try:
        Workout.objects.get(id=workout_id)
    except Workout.DoesNotExist:
        return redirect("/workout/")

    # Redirect to Django admin page for this workout
    return redirect(f"/admin/workout/workout/{workout_id}/change/")


def exercise_library(request):
    lang = translation.get_language()

    # Get filter parameters
    name = request.GET.get("name", "")
    muscle_group_id = request.GET.get("muscle_group", "")
    difficulty = request.GET.get("difficulty", "")
    equipment_id = request.GET.get("equipment", "")

    # Start with all exercises
    exercises = (
        Exercice.objects.all()
        .prefetch_related("muscle_groups", "equipment")
        .order_by("name")
    )

    # Apply filters
    if name:
        exercises = exercises.filter(name__icontains=name)
    if muscle_group_id:
        exercises = exercises.filter(muscle_groups__id=muscle_group_id)
    if difficulty:
        exercises = exercises.filter(difficulty=difficulty)
    if equipment_id:
        exercises = exercises.filter(equipment__id=equipment_id)

    # Get all muscle groups and equipment for filter dropdowns
    muscle_groups = MuscleGroup.objects.all().order_by("name")
    difficulties = Exercice.DIFFICULTY_CHOICES
    equipments = Equipment.objects.all().order_by("name")

    # Check if it's an AJAX request
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    context = {
        "page": "exercise_library",
        "lang": lang,
        "exercises": exercises,
        "muscle_groups": muscle_groups,
        "difficulties": difficulties,
        "equipments": equipments,
        "selected_name": name,
        "selected_muscle_group": muscle_group_id,
        "selected_difficulty": difficulty,
        "selected_equipment": equipment_id,
        "translations": {
            "exercise_library": gettext("Exercise Library"),
            "filters": gettext("Filters"),
            "muscle_group": gettext("Muscle Group"),
            "difficulty": gettext("Difficulty"),
            "equipment": gettext("Equipment"),
            "all": gettext("All"),
            "no_exercises": gettext("No exercises found."),
        },
    }

    if is_ajax:
        # Return only the exercises grid HTML for AJAX requests
        from django.template.loader import render_to_string

        exercises_html = render_to_string(
            "workout/exercise_library_grid.html", context, request=request
        )
        return JsonResponse({"exercises_html": exercises_html})

    return render(request, "exercise_library.html", context)


@login_required
def export_data(request):
    """Export all workout data to JSON file"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as tmp_file:
            tmp_path = tmp_file.name

        # Call the export command
        call_command("export_workout_data", output=tmp_path)

        # Read the file and return as download
        with open(tmp_path, "r", encoding="utf-8") as f:
            response = HttpResponse(f.read(), content_type="application/json")
            today_date = datetime.today().strftime("%Y-%m-%d")
            response["Content-Disposition"] = (
                f'attachment; filename="workout_data_{today_date}.json"'
            )

        # Clean up temp file
        os.unlink(tmp_path)

        return response
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def import_data(request):
    """Import workout data from JSON file"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    try:
        uploaded_file = request.FILES["file"]

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".json"
        ) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        # Call the import command
        call_command("import_workout_data", file=tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        return JsonResponse({"success": True, "message": "Data imported successfully"})
    except Exception as e:
        logger.error(f"Error importing data: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def clear_data(request):
    """Clear all workout data"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        # Call the clear command with no-input flag
        call_command("clear_workout_data", no_input=True)
        return JsonResponse(
            {"success": True, "message": "All data cleared successfully"}
        )
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_dashboard_data(request):
    """Get dashboard statistics filtered by date range (AJAX endpoint)"""
    from django.db.models import Count, F, Sum

    # Get date filter parameters
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    # Build filter
    workout_filter = {}
    if start_date:
        workout_filter["date__gte"] = start_date
    if end_date:
        workout_filter["date__lte"] = end_date

    # Build the filtered workout queryset
    filtered_workouts = (
        Workout.objects.filter(**workout_filter)
        if workout_filter
        else Workout.objects.all()
    )

    total_workouts = filtered_workouts.count()

    # Get exercise IDs from filtered workouts
    if workout_filter:
        filtered_workout_ids = filtered_workouts.values_list("id", flat=True)
        total_exercises = OneExercice.objects.filter(
            seance_id__in=filtered_workout_ids
        ).count()

        # Calculate total volume (for strength exercises) with date filter
        total_volume = (
            StrengthExerciseLog.objects.filter(
                workout_id__in=filtered_workout_ids
            ).aggregate(total=Sum(F("nb_series") * F("nb_repetition") * F("weight")))[
                "total"
            ]
            or 0
        )

        # Workouts by type with date filter
        workouts_by_type = list(
            filtered_workouts.values("type_workout__name_workout")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Top exercises by frequency with date filter
        top_exercises = list(
            OneExercice.objects.filter(seance_id__in=filtered_workout_ids)
            .values("name__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
    else:
        total_exercises = OneExercice.objects.count()

        # Calculate total volume (for strength exercises)
        total_volume = (
            StrengthExerciseLog.objects.aggregate(
                total=Sum(F("nb_series") * F("nb_repetition") * F("weight"))
            )["total"]
            or 0
        )

        # Workouts by type
        workouts_by_type = list(
            Workout.objects.values("type_workout__name_workout")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Top exercises by frequency
        top_exercises = list(
            OneExercice.objects.values("name__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

    # Weekly workouts trend - use date filter for the range if provided
    if start_date and end_date:
        # Calculate weeks between start and end date
        from datetime import datetime as dt

        start_dt = dt.strptime(start_date, "%Y-%m-%d").date()
        end_dt = dt.strptime(end_date, "%Y-%m-%d").date()
        total_days = (end_dt - start_dt).days
        num_weeks = max(total_days // 7, 1)  # Show all weeks in the date range

        weekly_workouts = []
        for week in range(num_weeks):
            week_start = start_dt + timedelta(weeks=week)
            week_end = min(week_start + timedelta(days=6), end_dt)
            count = Workout.objects.filter(
                date__gte=week_start, date__lte=week_end
            ).count()
            weekly_workouts.append(
                {
                    "week": week + 1,
                    "count": count,
                    "start": week_start.strftime("%d/%m/%Y"),
                }
            )
    else:
        # Show all available data - calculate from earliest workout to now
        earliest_workout = Workout.objects.order_by("date").first()
        if earliest_workout:
            start_dt = earliest_workout.date
            end_dt = datetime.now().date()
            total_days = (end_dt - start_dt).days
            num_weeks = max(total_days // 7, 1)

            weekly_workouts = []
            for week in range(num_weeks):
                week_start = start_dt + timedelta(weeks=week)
                week_end = min(week_start + timedelta(days=6), end_dt)
                count = Workout.objects.filter(
                    date__gte=week_start, date__lte=week_end
                ).count()
                weekly_workouts.append(
                    {
                        "week": week + 1,
                        "count": count,
                        "start": week_start.strftime("%d/%m/%Y"),
                    }
                )
        else:
            # No workouts yet
            weekly_workouts = []

    return JsonResponse(
        {
            "total_workouts": total_workouts,
            "total_exercises": total_exercises,
            "total_volume": int(total_volume),
            "workouts_by_type": workouts_by_type,
            "weekly_workouts": weekly_workouts,
            "top_exercises": top_exercises,
        }
    )


def calculate_personal_records(limit=10):
    """
    Calculate personal records at runtime from StrengthExerciseLog data.

    Returns a list of personal records sorted by date achieved (most recent first).
    """
    from django.db.models import F

    # Get all strength exercise logs with calculated volume (only exercises with weight)
    logs = (
        StrengthExerciseLog.objects.select_related("exercise", "workout")
        .filter(weight__gt=0)  # Only include exercises with weight > 0
        .annotate(volume=F("nb_series") * F("nb_repetition") * F("weight"))
        .order_by("-workout__date")
    )

    # Track personal records for each exercise
    records_by_exercise: dict[int, dict[str, Any]] = {}
    all_records: list[dict[str, Any]] = []

    for log in logs:
        exercise_id = log.exercise.id

        if exercise_id not in records_by_exercise:
            records_by_exercise[exercise_id] = {
                "max_weight": None,
            }

        exercise_records = records_by_exercise[exercise_id]

        # Check for max weight record
        if (
            exercise_records["max_weight"] is None
            or log.weight > exercise_records["max_weight"]["value"]
        ):
            exercise_records["max_weight"] = {
                "exercise": log.exercise,
                "record_type": "max_weight",
                "value": log.weight,
                "date_achieved": log.workout.date,
                "workout": log.workout,
                "display_name": "Max Weight",
            }

    # Collect all records
    for _exercise_id, records in records_by_exercise.items():
        for _record_type, record_data in records.items():
            if record_data:
                all_records.append(record_data)

    # Sort by date achieved (most recent first) and limit
    all_records.sort(key=lambda x: x["date_achieved"], reverse=True)
    return all_records[:limit]


def get_calendar_data(request):
    """AJAX endpoint to get calendar data for a specific year"""
    import calendar as cal
    from collections import defaultdict

    from django.http import JsonResponse

    # Get year from URL parameter or use current year
    current_year = int(request.GET.get("year", datetime.now().year))
    current_month = datetime.now().month

    # Get all workouts for calendar view
    workouts = Workout.objects.filter(date__year=current_year).order_by("date")

    # Determine which years have workout data
    years_with_data = (
        Workout.objects.dates("date", "year")
        .values_list("date__year", flat=True)
        .distinct()
    )
    years_with_data_l = list(years_with_data)

    # Check if there's data for previous and next year
    has_prev_year_data = (current_year - 1) in years_with_data_l
    has_next_year_data = (current_year + 1) in years_with_data_l

    # Create calendar data structure
    calendar_data = defaultdict(list)
    for workout in workouts:
        month_key = f"{workout.date.year}-{workout.date.month:02d}"
        calendar_data[month_key].append(
            {
                "day": workout.date.day,
                "type": (
                    workout.type_workout.name_workout
                    if workout.type_workout
                    else "No Type"
                ),
                "duration": workout.duration,
                "id": workout.id,
            }
        )

    # Define translatable month names
    month_names = [
        gettext("January"),
        gettext("February"),
        gettext("March"),
        gettext("April"),
        gettext("May"),
        gettext("June"),
        gettext("July"),
        gettext("August"),
        gettext("September"),
        gettext("October"),
        gettext("November"),
        gettext("December"),
    ]

    months_data = []
    for month in range(1, 13):
        month_name = month_names[month - 1]
        month_key = f"{current_year}-{month:02d}"

        # Get first day of month and number of days
        first_day = datetime(current_year, month, 1)
        num_days = cal.monthrange(current_year, month)[1]
        start_weekday = first_day.weekday()

        # Get workouts for this month
        month_workouts = calendar_data.get(month_key, [])
        workout_days = {w["day"]: w for w in month_workouts}

        months_data.append(
            {
                "name": month_name,
                "number": month,
                "num_days": num_days,
                "start_weekday": start_weekday,
                "workout_days": workout_days,
                "is_current": month == current_month
                and current_year == datetime.now().year,
            }
        )

    return JsonResponse(
        {
            "year": current_year,
            "months": months_data,
            "has_prev_year_data": has_prev_year_data,
            "has_next_year_data": has_next_year_data,
        }
    )


def analytics(request):
    """Analytics page with calendar view, progress dashboard, and PR tracking"""
    import calendar as cal
    import json
    from collections import defaultdict

    from django.db.models import Count, F, Sum

    lang = translation.get_language()

    # Use current year for initial page load
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Get all workouts for calendar view
    workouts = Workout.objects.filter(date__year=current_year).order_by("date")

    # Determine which years have workout data
    years_with_data = (
        Workout.objects.dates("date", "year")
        .values_list("date__year", flat=True)
        .distinct()
    )
    years_with_data_l = list(years_with_data)

    # Check if there's data for previous and next year
    has_prev_year_data = (current_year - 1) in years_with_data_l
    has_next_year_data = (current_year + 1) in years_with_data_l

    # Create calendar data structure
    calendar_data = defaultdict(list)
    for workout in workouts:
        month_key = f"{workout.date.year}-{workout.date.month:02d}"
        calendar_data[month_key].append(
            {
                "day": workout.date.day,
                "type": (
                    workout.type_workout.name_workout
                    if workout.type_workout
                    else "No Type"
                ),
                "duration": workout.duration,
                "id": workout.id,
            }
        )

    # Dashboard statistics - start with all workouts for initial load
    total_exercises = OneExercice.objects.count()

    # Calculate total volume (for strength exercises)
    total_volume = (
        StrengthExerciseLog.objects.aggregate(
            total=Sum(F("nb_series") * F("nb_repetition") * F("weight"))
        )["total"]
        or 0
    )

    # Workouts by type
    workouts_by_type = list(
        Workout.objects.values("type_workout__name_workout")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Top exercises by frequency
    top_exercises = list(
        OneExercice.objects.values("name__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Total workouts for initial load
    total_workouts = Workout.objects.count()

    # Weekly workouts trend - calculate from earliest workout to now
    earliest_workout = Workout.objects.order_by("date").first()
    if earliest_workout:
        start_dt = earliest_workout.date
        end_dt = datetime.now().date()
        total_days = (end_dt - start_dt).days
        num_weeks = max(total_days // 7, 1)

        weekly_workouts = []
        for week in range(num_weeks):
            week_start = start_dt + timedelta(weeks=week)
            week_end = min(week_start + timedelta(days=6), end_dt)
            count = Workout.objects.filter(
                date__gte=week_start, date__lte=week_end
            ).count()
            weekly_workouts.append(
                {
                    "week": week + 1,
                    "count": count,
                    "start": week_start.strftime("%d/%m/%Y"),
                }
            )
    else:
        # No workouts yet
        weekly_workouts = []

    # Personal Records (calculated at runtime)
    personal_records = calculate_personal_records(limit=10)

    # Generate calendar months for the year
    # Define translatable month names
    month_names = [
        gettext("January"),
        gettext("February"),
        gettext("March"),
        gettext("April"),
        gettext("May"),
        gettext("June"),
        gettext("July"),
        gettext("August"),
        gettext("September"),
        gettext("October"),
        gettext("November"),
        gettext("December"),
    ]

    months_data = []
    for month in range(1, 13):
        month_name = month_names[month - 1]
        month_key = f"{current_year}-{month:02d}"

        # Get first day of month and number of days
        first_day = datetime(current_year, month, 1)
        num_days = cal.monthrange(current_year, month)[1]
        start_weekday = first_day.weekday()

        # Get workouts for this month
        month_workouts = calendar_data.get(month_key, [])
        workout_days = {w["day"]: w for w in month_workouts}

        months_data.append(
            {
                "name": month_name,
                "number": month,
                "num_days": num_days,
                "start_weekday": start_weekday,
                "workout_days": workout_days,
                "is_current": month == current_month,
            }
        )

    context = {
        "page": "analytics",
        "lang": lang,
        "current_year": current_year,
        "months": months_data,
        "has_prev_year_data": has_prev_year_data,
        "has_next_year_data": has_next_year_data,
        "total_workouts": total_workouts,
        "total_exercises": total_exercises,
        "total_volume": int(total_volume),
        "workouts_by_type": json.dumps(workouts_by_type),
        "weekly_workouts": json.dumps(weekly_workouts),
        "personal_records": personal_records,
        "top_exercises": json.dumps(top_exercises),
        "translations": {
            "analytics": gettext("Analytics"),
            "calendar": gettext("Calendar"),
            "dashboard": gettext("Dashboard"),
            "personal_records": gettext("Personal Records"),
            "total_workouts": gettext("Total Workouts"),
            "total_exercises": gettext("Total Exercises"),
            "total_volume": gettext("Total Volume"),
            "current_streak": gettext("Current Streak"),
            "longest_streak": gettext("Longest Streak"),
            "workouts_by_type": gettext("Workouts by Type"),
            "weekly_trend": gettext("Weekly Trend"),
            "top_exercises": gettext("Top Exercises"),
        },
    }

    return render(request, "workout/analytics.html", context)
