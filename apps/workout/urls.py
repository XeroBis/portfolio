from django.shortcuts import redirect
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.redirect_workout, name="workout"),
    path("get_last_workout/", views.get_last_workout, name="get_last_workout"),
    path("get_list_exercice/", views.get_list_exercise, name="get_list_exercise"),
    path("get_workout_types/", views.get_workout_types, name="get_workout_types"),
    path("add_workout/", views.add_workout, name="add_workout"),
    path("edit_workout/<int:workout_id>/", views.edit_workout, name="edit_workout"),
    path(
        "create_template/<int:workout_id>/",
        views.create_template_from_workout,
        name="create_template",
    ),
    path("get_template_list/", views.get_template_list, name="get_template_list"),
    path(
        "get_template_details/", views.get_template_details, name="get_template_details"
    ),
    path("library/", views.exercise_library, name="exercise_library"),
    path("analytics/", views.analytics, name="analytics"),
    path("get_dashboard_data/", views.get_dashboard_data, name="get_dashboard_data"),
    path("get_calendar_data/", views.get_calendar_data, name="get_calendar_data"),
    path("export_data/", views.export_data, name="export_data"),
    path("import_data/", views.import_data, name="import_data"),
    path("clear_data/", views.clear_data, name="clear_data"),
    re_path(r"^.*$", lambda request: redirect("workout"), name="catch_all"),
]
