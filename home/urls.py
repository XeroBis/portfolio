from django.urls import path

from . import views

urlpatterns = [
    path("<str:lang>/", views.home, name="home"),
    path("<str:lang>/workout/", views.redirect_workout, name="redirect_workout"),
    path("", views.redirect_view, name="redirect_view"),
    path("<str:lang>/<str:any>", views.redirect_view, name="redirect_view"),
]