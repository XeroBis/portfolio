from django.urls import path, re_path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path("", views.redirect_workout, name="workout"),
    path("get_last_workout/", views.get_last_workout, name="get_last_workout"),
    path("get_list_exercice/", views.get_list_exercise, name="get_list_exercise"),
    path("get_workout_types/", views.get_workout_types, name="get_workout_types"),
    path("add_workout/", views.add_workout, name='add_workout'),
    re_path(r'^.*$', lambda request: redirect('workout'), name='catch_all'),
]