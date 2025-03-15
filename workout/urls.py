from django.urls import path

from . import views

urlpatterns = [
    path("", views.redirect_workout, name="workout"),
    path("get_last_workout/", views.get_last_workout, name="get_last_workout"),
    path("get_list_exercice/", views.get_list_exercise, name="get_list_exercise"),
    path("add_workout/", views.add_workout, name='add_workout'),
    path("ajout_seance/", views.add_workout, name='add_workout'),
]