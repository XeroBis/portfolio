from django.urls import path
from . import views

app_name = 'newsfeed'

urlpatterns = [
    path('', views.home, name='home'),
    path('fetch/', views.fetch_feeds, name='fetch_feeds'),
]