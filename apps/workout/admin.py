from django.contrib import admin

# Register your models here.
from .models import TypeWorkout, Workout, Exercice, OneExercice

admin.site.register(TypeWorkout)
admin.site.register(Workout)
admin.site.register(Exercice)
admin.site.register(OneExercice)
