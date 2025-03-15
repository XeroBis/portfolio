from django.shortcuts import render, redirect 

from .models import Projet, Testimonial


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

