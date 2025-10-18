from django.contrib import admin

# Register your models here.
from .models import Projet, Tag, Testimonial

admin.site.register(Tag)
admin.site.register(Projet)
admin.site.register(Testimonial)
