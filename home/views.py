from django.shortcuts import render, get_object_or_404

from .models import Projet

def home(request):
    """
    View pour afficher la page d'accueil.
    """
    projets = Projet.objects.all()
    context = {"projets":projets}
    return render(request, 'index.html', context)

