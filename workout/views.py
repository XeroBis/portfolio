from django.shortcuts import render, redirect 
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Workout, OneExercice, TypeWorkout, Exercice


def redirect_workout(request):
    url_path = request.get_full_path().split("/")
    lang = url_path[1]

    if lang not in ["fr", "en"]:
        return redirect("/fr/sports/")
    workouts = Workout.objects.all().order_by('-date')
    paginator = Paginator(workouts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    workout_data = []
    for workout in page_obj:
        exercises = OneExercice.objects.filter(seance=workout)
        workout_data.append({
            'workout': {
                'id': workout.id,
                'date': workout.date.strftime('%-d/%m/%Y'),
                'type_workout': workout.type_workout.name
            },
            'exercises': [
                {
                    'id': exercise.id,
                    'name': exercise.name.name if exercise else None,
                    'nb_series': exercise.nb_series,
                    'nb_repetition': exercise.nb_repetition,
                    'weight': exercise.weight,
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
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None
    }
    return render(request, 'workout.html', context)


@login_required
def add_workout(request):
    url_path = request.get_full_path().split("/")
    lang = url_path[1]
    if lang not in ["fr", "en"]:
        return redirect("/fr/sports/")
    
    if request.method == 'POST':
        date = request.POST['date']
        type_workout = request.POST['type_workout']

        type = TypeWorkout.objects.filter(name=type_workout).first()
        
        workout = Workout(date=date, type_workout=type)
        workout.save()
        
        for key, value in request.POST.items():
            if key.startswith('exercise_') and key.endswith('_name'):
                exercise_id = key.split('_')[1]
                exercise_name = value
                nb_series = request.POST.get(f'exercise_{exercise_id}_nb_series')
                nb_repetition = request.POST.get(f'exercise_{exercise_id}_nb_repetition')
                weight = request.POST.get(f'exercise_{exercise_id}_weight')
                
                exercise = OneExercice(
                    name=Exercice.objects.get(name=exercise_name),
                    seance=workout,
                    nb_series=nb_series,
                    nb_repetition=nb_repetition,
                    weight=weight,
                )
                exercise.save()
        
        if lang == "en":
            return redirect(f'/en/workout')
        else:
            return redirect(f'/fr/sports')
    
    context = {"page": "add_workout", "lang": lang}
    return render(request, 'add_workout.html', context)


@login_required
def get_last_workout(request):
    workout_type = request.GET.get('type')
    workout_type_id = TypeWorkout.objects.filter(name=workout_type).first()
    last_workout = Workout.objects.filter(type_workout=workout_type_id).order_by('-date').first()
    
    all_exercises = Exercice.objects.all().order_by("name").values_list('name', flat=True)

    if last_workout:
        exercises = OneExercice.objects.filter(seance=last_workout)
        exercises_data = []
        for exercise in exercises:
            exercises_data.append({
                'name': exercise.name.name,
                'nb_series': exercise.nb_series,
                'nb_repetition': exercise.nb_repetition,
                'weight': exercise.weight,
            })
        
        data = {
            'date': last_workout.date.strftime('%Y-%m-%d'),
            'exercises': exercises_data,
            "all_exercises":list(all_exercises)
        }
    else:
        data = {}
    
    return JsonResponse(data)


@login_required
def get_list_exercise(request):
    all_exercises = Exercice.objects.all().order_by("name").values_list('name', flat=True)
    data = {"all_exercises":list(all_exercises)}
    return JsonResponse(data)
