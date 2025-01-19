from django.shortcuts import render
from django.shortcuts import redirect

from .models import Projet, Testimonial

def home(request, lang):
    """
    View pour afficher la page d'accueil.
    """
    if lang not in ["fr", "en"]:
        return redirect('/fr/')
    projets = Projet.objects.all()
    testimonial = Testimonial.objects.all()
    context = {"projets":projets, "lang":lang, "testimonials":testimonial}
    return render(request, 'index.html', context)



def redirect_view(request, lang=None, any=None):
    if lang is not None:
        response = redirect(f'/{lang}/')
        # on repasse dans la fonction home pour check si lang == en ou fr
    else:
        response = redirect('/fr/')
    return response