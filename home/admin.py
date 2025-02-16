from django.contrib import admin

# Register your models here.
from .models import Tag, Projet, Testimonial, TypeWorkout, Workout, Exercice, OneExercice

admin.site.register(Tag)
admin.site.register(Projet)
admin.site.register(Testimonial)

admin.site.register(TypeWorkout)
admin.site.register(Workout)
admin.site.register(Exercice)
admin.site.register(OneExercice)

