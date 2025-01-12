from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Projet

def home(request, lang):
    """
    View pour afficher la page d'accueil.
    """
    if lang not in ["fr", "en"]:
        return redirect('/fr/')
    projets = Projet.objects.all()
    context = {"projets":projets, "lang":lang}
    return render(request, 'index.html', context)



def redirect_view(request):
    response = redirect('/fr/')
    return response