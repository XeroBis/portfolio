"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("fr/sports/", include("workout.urls")),
    path("en/workout/", include("workout.urls")),
    path("fr/", include("home.urls")),
    path("en/", include("home.urls")),
    re_path(r".*", include("home.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
