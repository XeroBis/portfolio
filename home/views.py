from django.shortcuts import render, redirect 
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Projet, Testimonial, Workout, OneExercice

def home(request, lang):
    """
    View pour afficher la page d'accueil.
    """
    if lang not in ["fr", "en"]:
        return redirect('/fr/')
    projets = Projet.objects.all()
    testimonial = Testimonial.objects.all()
    context = {"page":"home", "projets":projets, "lang":lang, "testimonials":testimonial}
    return render(request, 'home.html', context)



def redirect_view(request, lang=None, any=None):

    url = "/fr/"

    if lang is not None and lang in ["fr", "en"]:
        url = f"/{lang}/"
    
    if any is not None and any in ["workout"]:
        url += "workout/"

    return redirect(url)


def redirect_workout(request, lang):
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