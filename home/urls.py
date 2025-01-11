from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projet/<int:projet_id>/", views.projet, name="projet")
]