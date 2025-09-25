from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import gettext

from .models import Workout, OneExercice, TypeWorkout, Exercice, StrengthExerciseLog, CardioExerciseLog
from django.contrib.contenttypes.models import ContentType


def redirect_workout(request):
    lang = translation.get_language()

    workouts = Workout.objects.all().order_by('-date')
    paginator = Paginator(workouts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    workout_data = []
    for workout in page_obj:
        exercises = OneExercice.objects.filter(seance=workout)
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
            "distance_m": gettext("Distance (m)")
        }
    }
    return render(request, 'workout.html', context)


@login_required
def add_workout(request):
    lang = translation.get_language()

    if request.method == 'POST':
        date = request.POST['date']
        type_workout = request.POST['type_workout']
        duration = request.POST['duration']

        type, _= TypeWorkout.objects.get_or_create(name_workout=type_workout)

        workout = Workout(date=date, type_workout=type, duration=duration)
        workout.save()

        for key, value in request.POST.items():
            if key.startswith('exercise_') and key.endswith('_name'):
                exercise_id = key.split('_')[1]
                exercise_name = value
                exercise_obj = Exercice.objects.get(name=exercise_name)

                # Create specific exercise log based on type
                if exercise_obj.exercise_type == 'strength':
                    nb_series = request.POST.get(f'exercise_{exercise_id}_nb_series')
                    nb_repetition = request.POST.get(f'exercise_{exercise_id}_nb_repetition')
                    weight = request.POST.get(f'exercise_{exercise_id}_weight')

                    exercise_log = StrengthExerciseLog.objects.create(
                        exercise=exercise_obj,
                        workout=workout,
                        nb_series=nb_series,
                        nb_repetition=nb_repetition,
                        weight=weight,
                    )
                    content_type = ContentType.objects.get_for_model(StrengthExerciseLog)

                elif exercise_obj.exercise_type == 'cardio':
                    duration_seconds = request.POST.get(f'exercise_{exercise_id}_duration_seconds')
                    distance_m = request.POST.get(f'exercise_{exercise_id}_distance_m')

                    exercise_log = CardioExerciseLog.objects.create(
                        exercise=exercise_obj,
                        workout=workout,
                        duration_seconds=duration_seconds,
                        distance_m=distance_m,
                    )
                    content_type = ContentType.objects.get_for_model(CardioExerciseLog)

                # Create the polymorphic OneExercice entry
                one_exercise = OneExercice.objects.create(
                    name=exercise_obj,
                    seance=workout,
                    content_type=content_type,
                    object_id=exercise_log.id,
                )

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
        exercises = OneExercice.objects.filter(seance=last_workout)
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
