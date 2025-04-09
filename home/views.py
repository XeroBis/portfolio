from django.shortcuts import render, redirect 

from .models import Projet, Tag, Testimonial
from workout.models import TypeWorkout, Workout, Exercice, OneExercice
import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

def home(request):
    """
    View pour afficher la page d'accueil.
    """
    url_path = request.get_full_path().split("/")
    lang = url_path[1]

    if lang not in ["fr", "en"]:
        return redirect('/fr/') # langue par défaut
    if len(url_path)>3 :
        return redirect("/"+lang+"/")
    projets = Projet.objects.all()
    testimonial = Testimonial.objects.all()
    context = {"page":"home", "projets":projets, "lang":lang, "testimonials":testimonial}
    return render(request, 'home.html', context)

@login_required
def download_data_json(request):
    data = {
        "tags": list(Tag.objects.values()),
        "projects": [
            {
                "title_en": proj.title_en,
                "description_en": proj.description_en,
                "title_fr": proj.title_fr,
                "description_fr": proj.description_fr,
                "github_url": proj.github_url,
                "tags": list(proj.tags.values_list("id", flat=True))
            }
            for proj in Projet.objects.all()
        ],
        "testimonials": list(Testimonial.objects.values()),
        "type_workouts": list(TypeWorkout.objects.values()),
        "workouts": [
            {"date": workout.date.strftime("%Y-%m-%d"), "type_workout": workout.type_workout_id, "duration": workout.duration}
            for workout in Workout.objects.all()
        ],
        "exercises": list(Exercice.objects.values()),
        "one_exercises": [
            {"name": one_ex.name_id, "seance": one_ex.seance.date.strftime("%Y-%m-%d"), "nb_series": one_ex.nb_series, "nb_repetition": one_ex.nb_repetition, "weight": one_ex.weight}
            for one_ex in OneExercice.objects.all()
        ]
    }

    response = HttpResponse(json.dumps(data, indent=4, ensure_ascii=False), content_type="application/json")
    response["Content-Disposition"] = "attachment; filename=data.json"
    return response

@login_required
def import_data_json(request):
    if request.method == "POST" and request.FILES.get("file"):
        try:
            json_file = request.FILES["file"]
            data = json.load(json_file)

            tag_objects = {tag["id"]: Tag.objects.get_or_create(id=tag["id"], defaults={"name": tag["name"]})[0] for tag in data.get("tags", [])}

            for project in data.get("projects", []):
                obj, _ = Projet.objects.update_or_create(
                    title_en=project["title_en"],
                    defaults={
                        "description_en": project["description_en"],
                        "title_fr": project["title_fr"],
                        "description_fr": project["description_fr"],
                        "github_url": project["github_url"]
                    }
                )
                obj.tags.set([tag_objects[tag_id] for tag_id in project.get("tags", [])])


            for testimonial in data.get("testimonials", []):
                Testimonial.objects.update_or_create(
                    author=testimonial["author"],
                    defaults={
                        "text_en": testimonial["text_en"],
                        "text_fr": testimonial["text_fr"]
                    }
                )

            type_workout_objects = {tw["id"]: TypeWorkout.objects.get_or_create(id=tw["id"], defaults={"name": tw["name"]})[0] for tw in data.get("type_workouts", [])}

            workout_objects = {}
            for workout in data.get("workouts", []):
                obj, created = Workout.objects.update_or_create(
                    date=workout["date"],
                    defaults={
                        "type_workout": type_workout_objects.get(workout["type_workout"]),
                        "duration": workout["duration"]
                    }
                )
                workout_objects[workout["date"]] = obj

            exercice_objects = {ex["id"]: Exercice.objects.get_or_create(id=ex["id"], defaults={"name": ex["name"]})[0] for ex in data.get("exercises", [])}
            for one_ex in data.get("one_exercises", []):
                OneExercice.objects.update_or_create(
                    name=exercice_objects[one_ex["name"]],
                    seance=workout_objects.get(one_ex["seance"]),
                    defaults={
                        "nb_series": one_ex["nb_series"],
                        "nb_repetition": one_ex["nb_repetition"],
                        "weight": one_ex["weight"]
                    }
                )

            url_path = request.get_full_path().split("/")
            lang = url_path[1]

            if lang not in ["fr", "en"]:
                return redirect('/fr/') # langue par défaut
            
            return redirect("/"+lang+"/")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def reset_data(request):
    try:
        Tag.objects.all().delete()
        Projet.objects.all().delete()
        Testimonial.objects.all().delete()
        TypeWorkout.objects.all().delete()
        Workout.objects.all().delete()
        Exercice.objects.all().delete()
        OneExercice.objects.all().delete()

        url_path = request.get_full_path().split("/")
        lang = url_path[1]
        if lang not in ["fr", "en"]:
            return redirect('/fr/')
            
        return redirect("/"+lang+"/")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)