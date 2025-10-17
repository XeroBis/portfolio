from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import gettext
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
import logging
import json
from datetime import datetime
import os
import tempfile

from .models import Workout, OneExercice, TypeWorkout, Exercice, StrengthExerciseLog, CardioExerciseLog, MuscleGroup, Equipment
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


def redirect_workout(request):
    lang = translation.get_language()

    workouts = Workout.objects.all().order_by('-date')
    paginator = Paginator(workouts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    workout_data = []
    for workout in page_obj:
        exercises = OneExercice.objects.filter(seance=workout).order_by('position')
        type_workout = workout.type_workout.name_workout
        workout_data.append({
            'workout': {
                'id': workout.id,
                'date': workout.date.strftime('%-d/%m/%Y'),
                'type_workout': type_workout,
                'duration':workout.duration
            },
            'exercises': [
                {
                    'id': exercise.id,
                    'name': exercise.name.name if exercise else None,
                    'exercise_type': exercise.name.exercise_type,
                    'data': exercise.get_display_data(),
                    'muscle_groups': list(exercise.name.muscle_groups.all().values_list('name', flat=True))
                }
                for exercise in exercises
            ]
        })

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        data = {
            'workout_data': workout_data,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
        }
        return JsonResponse(data)

    context = {
        "page": "workout",
        "lang": lang,
        "workout_data": workout_data,
        "has_next": page_obj.has_next(),
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        "translations": {
            "exercise": gettext("Exercise"),
            "exercice": gettext("Exercise"),
            "series": gettext("Series"),
            "reps": gettext("Reps"),
            "weight_kg": gettext("Weight (kg)"),
            "duration_min": gettext("Duration (min)"),
            "distance_m": gettext("Distance (m)"),
            "edit": gettext("Edit")
        }
    }
    return render(request, 'workout.html', context)


@login_required
def add_workout(request):
    lang = translation.get_language()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                date = request.POST['date']
                type_workout = request.POST['type_workout']
                duration = request.POST['duration']

                type_obj, _ = TypeWorkout.objects.get_or_create(name_workout=type_workout)

                workout = Workout.objects.create(
                    date=date,
                    type_workout=type_obj,
                    duration=duration
                )

                # Process exercises in order to avoid duplicates
                exercise_data = {}
                for key, value in request.POST.items():
                    if key.startswith('exercise_') and key.endswith('_name'):
                        exercise_id = key.split('_')[1]
                        if exercise_id not in exercise_data:
                            exercise_data[exercise_id] = {'name': value}
                    elif key.startswith('exercise_') and not key.endswith('_name'):
                        parts = key.split('_')
                        if len(parts) >= 3:
                            exercise_id = parts[1]
                            field_name = '_'.join(parts[2:])
                            if exercise_id not in exercise_data:
                                exercise_data[exercise_id] = {}
                            exercise_data[exercise_id][field_name] = value

                # Create exercise logs for each unique exercise
                logger.info(f"Processing {len(exercise_data)} exercises for workout {workout.id}")

                # Sort exercises by their ID to maintain order
                sorted_exercises = sorted(exercise_data.items(), key=lambda x: int(x[0]))

                for position, (exercise_id, data) in enumerate(sorted_exercises, start=1):
                    logger.info(f"Processing exercise_id: {exercise_id}, data: {data}, position: {position}")

                    if 'name' not in data:
                        logger.warning(f"Exercise {exercise_id} missing name, skipping")
                        continue

                    try:
                        exercise_obj = Exercice.objects.get(name=data['name'])
                        logger.info(f"Found exercise: {exercise_obj.name} (type: {exercise_obj.exercise_type})")
                    except Exercice.DoesNotExist:
                        logger.warning(f"Exercise '{data['name']}' not found in database, skipping")
                        continue

                    # Create specific exercise log based on type
                    if exercise_obj.exercise_type == 'strength':
                        logger.info(f"Creating StrengthExerciseLog for exercise: {exercise_obj.name}, workout: {workout.id}")
                        exercise_log, created = StrengthExerciseLog.objects.get_or_create(
                            exercise=exercise_obj,
                            workout=workout,
                            defaults={
                                'nb_series': data.get('nb_series', 0),
                                'nb_repetition': data.get('nb_repetition', 0),
                                'weight': data.get('weight', 0),
                            }
                        )
                        logger.info(f"StrengthExerciseLog {'created' if created else 'retrieved'}: {exercise_log.id}")
                        content_type = ContentType.objects.get_for_model(StrengthExerciseLog)

                    elif exercise_obj.exercise_type == 'cardio':
                        logger.info(f"Creating CardioExerciseLog for exercise: {exercise_obj.name}, workout: {workout.id}")
                        exercise_log, created = CardioExerciseLog.objects.get_or_create(
                            exercise=exercise_obj,
                            workout=workout,
                            defaults={
                                'duration_seconds': data.get('duration_seconds'),
                                'distance_m': data.get('distance_m'),
                            }
                        )
                        logger.info(f"CardioExerciseLog {'created' if created else 'retrieved'}: {exercise_log.id}")
                        content_type = ContentType.objects.get_for_model(CardioExerciseLog)

                    # Create the polymorphic OneExercice entry only if it doesn't exist
                    logger.info(f"Creating OneExercice entry for exercise: {exercise_obj.name} at position {position}")
                    one_exercice, created = OneExercice.objects.get_or_create(
                        name=exercise_obj,
                        seance=workout,
                        position=position,
                        defaults={
                            'content_type': content_type,
                            'object_id': exercise_log.id,
                        }
                    )
                    logger.info(f"OneExercice {'created' if created else 'retrieved'}: {one_exercice.id}")

        except Exception as e:
            # If there's any error, redirect back to form with error handling
            logger.error(f"Error creating workout: {str(e)}", exc_info=True)
            return redirect('/workout/add_workout/')

        return redirect('/workout/')

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
            "distance_m": gettext("Distance (m)")
        }
    }
    return render(request, 'add_workout.html', context)


@login_required
def get_last_workout(request):
    workout_type = request.GET.get('type')
    workout_type_id = TypeWorkout.objects.filter(name_workout=workout_type).first()
    last_workout = Workout.objects.filter(type_workout=workout_type_id).order_by('-date').first()
    
    all_exercises = Exercice.objects.all().order_by("name").values('name', 'exercise_type')

    if last_workout:
        exercises = OneExercice.objects.filter(seance=last_workout).order_by('position')
        exercises_data = []
        for exercise in exercises:
            exercise_data = {
                'name': exercise.name.name,
                'exercise_type': exercise.name.exercise_type,
            }
            exercise_data.update(exercise.get_display_data())
            exercises_data.append(exercise_data)

        data = {
            'date': last_workout.date.strftime('%Y-%m-%d'),
            'exercises': exercises_data,
            "all_exercises": list(all_exercises)
        }
    else:
        data = {
            "all_exercises": list(all_exercises)
        }
    
    return JsonResponse(data)


@login_required
def get_list_exercise(request):
    all_exercises = Exercice.objects.all().order_by("name").values('name', 'exercise_type')
    data = {"all_exercises": list(all_exercises)}
    return JsonResponse(data)


@login_required
def get_workout_types(request):
    lang = translation.get_language()
    workout_types = TypeWorkout.objects.all().order_by("name_workout")

    workout_types_data = []
    for workout_type in workout_types:
        workout_types_data.append({
            'value': workout_type.name_workout,
            'display': workout_type.name_workout
        })

    data = {"workout_types": workout_types_data}
    return JsonResponse(data)


@login_required
def edit_workout(request, workout_id):
    try:
        workout = Workout.objects.get(id=workout_id)
    except Workout.DoesNotExist:
        return redirect('/workout/')

    # Redirect to Django admin page for this workout
    return redirect(f'/admin/workout/workout/{workout_id}/change/')


def exercise_library(request):
    lang = translation.get_language()

    # Get filter parameters
    name = request.GET.get('name', '')
    muscle_group_id = request.GET.get('muscle_group', '')
    difficulty = request.GET.get('difficulty', '')
    equipment_id = request.GET.get('equipment', '')

    # Start with all exercises
    exercises = Exercice.objects.all().prefetch_related('muscle_groups', 'equipment').order_by('name')

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
    muscle_groups = MuscleGroup.objects.all().order_by('name')
    difficulties = Exercice.DIFFICULTY_CHOICES
    equipments = Equipment.objects.all().order_by('name')

    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

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
        }
    }

    if is_ajax:
        # Return only the exercises grid HTML for AJAX requests
        from django.template.loader import render_to_string
        exercises_html = render_to_string('workout/exercise_library_grid.html', context, request=request)
        return JsonResponse({'exercises_html': exercises_html})

    return render(request, 'exercise_library.html', context)


@login_required
def export_data(request):
    """Export all workout data to JSON file"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_path = tmp_file.name

        # Call the export command
        call_command('export_workout_data', output=tmp_path)

        # Read the file and return as download
        with open(tmp_path, 'r', encoding='utf-8') as f:
            response = HttpResponse(f.read(), content_type='application/json')
            today_date = datetime.today().strftime('%Y-%m-%d')
            response['Content-Disposition'] = f'attachment; filename="workout_data_{today_date}.json"'

        # Clean up temp file
        os.unlink(tmp_path)

        return response
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def import_data(request):
    """Import workout data from JSON file"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    try:
        uploaded_file = request.FILES['file']

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        # Call the import command
        call_command('import_workout_data', file=tmp_path)

        # Clean up temp file
        os.unlink(tmp_path)

        return JsonResponse({'success': True, 'message': 'Data imported successfully'})
    except Exception as e:
        logger.error(f"Error importing data: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def clear_data(request):
    """Clear all workout data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    try:
        # Call the clear command with no-input flag
        call_command('clear_workout_data', no_input=True)
        return JsonResponse({'success': True, 'message': 'All data cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
