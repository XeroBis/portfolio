from django.urls import path, re_path
from django.shortcuts import redirect
from . import views

app_name = 'newsfeed'

urlpatterns = [
    path('', views.home, name='home'),
    path('fetch/', views.fetch_feeds, name='fetch_feeds'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('export/', views.export_rss_feeds, name='export_feeds'),
    path('import/', views.import_rss_feeds, name='import_feeds'),
    path('delete-articles/', views.delete_articles, name='delete_articles'),
    path('delete-feeds/', views.delete_feeds, name='delete_feeds'),
    path('clear-all/', views.clear_all, name='clear_all'),
    re_path(r'^.*$', lambda request: redirect('newsfeed:home'), name='catch_all'),
]