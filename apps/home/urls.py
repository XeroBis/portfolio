from django.urls import path, re_path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path("export_data/", views.download_data_json, name="export_data"),
    path("import_data/", views.import_data_json, name="import_data"),
    path("reset_data/", views.reset_data, name="reset_data"),
    path("", views.home, name="home"),
    re_path(r'^.*$', lambda request: redirect('home'), name='catch_all'),
]