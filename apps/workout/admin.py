from django.contrib import admin
from .models import (
    TypeWorkout, Workout, Exercice, OneExercice,
    StrengthExerciseLog, CardioExerciseLog
)


@admin.register(TypeWorkout)
class TypeWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_workout')
    search_fields = ('name_workout',)
    ordering = ('name_workout',)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'type_workout', 'duration_minutes')
    list_filter = ('date', 'type_workout')
    search_fields = ('date', 'type_workout__name_workout')
    date_hierarchy = 'date'
    ordering = ('-date',)

    def duration_minutes(self, obj):
        return f"{obj.duration} min"
    duration_minutes.short_description = 'Duration'


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'exercise_type')
    list_filter = ('exercise_type',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(OneExercice)
class OneExerciceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seance', 'seance_date', 'exercise_details')
    list_filter = ('seance__date', 'name__exercise_type')
    search_fields = ('name__name', 'seance__date')
    raw_id_fields = ('name', 'seance')
    ordering = ('-seance__date',)

    def seance_date(self, obj):
        return obj.seance.date if obj.seance else "No Date"
    seance_date.short_description = 'Workout Date'

    def exercise_details(self, obj):
        if obj.exercise_log:
            if hasattr(obj.exercise_log, 'nb_series'):
                return f"{obj.exercise_log.nb_series}x{obj.exercise_log.nb_repetition} @ {obj.exercise_log.weight}kg"
            elif hasattr(obj.exercise_log, 'duration_seconds'):
                distance = f" - {obj.exercise_log.distance_m}m" if obj.exercise_log.distance_m else ""
                return f"{obj.exercise_log.duration_seconds}s{distance}"
        return "No details"
    exercise_details.short_description = 'Details'


@admin.register(StrengthExerciseLog)
class StrengthExerciseLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise', 'workout', 'workout_date', 'nb_series', 'nb_repetition', 'weight')
    list_filter = ('workout__date', 'exercise')
    search_fields = ('exercise__name', 'workout__date')
    raw_id_fields = ('exercise', 'workout')
    ordering = ('-workout__date',)

    def workout_date(self, obj):
        return obj.workout.date if obj.workout else "No Date"
    workout_date.short_description = 'Workout Date'


@admin.register(CardioExerciseLog)
class CardioExerciseLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise', 'workout', 'workout_date', 'duration_minutes', 'distance_m')
    list_filter = ('workout__date', 'exercise')
    search_fields = ('exercise__name', 'workout__date')
    raw_id_fields = ('exercise', 'workout')
    ordering = ('-workout__date',)

    def workout_date(self, obj):
        return obj.workout.date if obj.workout else "No Date"
    workout_date.short_description = 'Workout Date'

    def duration_minutes(self, obj):
        return f"{obj.duration_seconds}s" if obj.duration_seconds else "No duration"
    duration_minutes.short_description = 'Duration'
