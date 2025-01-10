from django.shortcuts import render


def home(request):
    """
    View pour afficher la page d'accueil.
    """
    return render(request, 'index.html')
