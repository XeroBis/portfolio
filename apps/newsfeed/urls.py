from django.urls import path
from . import views

app_name = 'newsfeed'

urlpatterns = [
    path('', views.home, name='home'),
    path('fetch/', views.fetch_feeds, name='fetch_feeds'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('export/', views.export_rss_feeds, name='export_feeds'),
    path('import/', views.import_rss_feeds, name='import_feeds'),
]