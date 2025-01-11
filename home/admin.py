from django.contrib import admin

# Register your models here.
from .models import Tag, Projet

admin.site.register(Tag)
admin.site.register(Projet)