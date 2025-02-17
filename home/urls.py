from django.urls import path

from . import views

urlpatterns = [
    path("get_last_workout/", views.get_last_workout, name="get_last_workout"),
    path("get_list_exercice/", views.get_list_exercise, name="get_list_exercise"),
    path("<str:lang>/", views.home, name="home"),
    path("<str:lang>/workout/", views.redirect_workout, name="redirect_workout"),
    path("<str:lang>/sports/", views.redirect_workout, name="redirect_workout"),
    path("<str:lang>/add_workout/", views.add_workout, name='add_workout'),
    path("<str:lang>/ajout_seance/", views.add_workout, name='add_workout'),
    path("<str:lang>/login/", views.user_login, name="user_login"),
    path("<str:lang>/logout/", views.user_logout, name="user_logout"),
    path("", views.redirect_view, name="redirect_view"),
    path("<str:lang>/<str:any>", views.redirect_view, name="redirect_view"),
]