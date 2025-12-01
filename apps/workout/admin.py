from django.contrib import admin

from .models import (
    CardioSeriesLog,
    Equipment,
    Exercice,
    MuscleGroup,
    OneExercice,
    StrengthSeriesLog,
    TypeWorkout,
    Workout,
)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
    list_filter = ["name"]


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
    list_filter = ["name"]


@admin.register(TypeWorkout)
class TypeWorkoutAdmin(admin.ModelAdmin):
    list_display = ["name_workout"]
    search_fields = ["name_workout"]
    list_filter = ["name_workout"]


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "exercise_type",
        "difficulty",
        "get_muscle_groups",
        "get_equipment",
    ]
    search_fields = ["name"]
    list_filter = ["exercise_type", "difficulty"]
    filter_horizontal = ["muscle_groups", "equipment"]

    @admin.display(description="Muscle Groups")
    def get_muscle_groups(self, obj):
        return ", ".join([mg.name for mg in obj.muscle_groups.all()])

    @admin.display(description="Equipment")
    def get_equipment(self, obj):
        return ", ".join([eq.name for eq in obj.equipment.all()])


class StrengthSeriesLogInline(admin.TabularInline):
    model = StrengthSeriesLog
    extra = 1
    fields = ["exercise", "series_number", "reps", "weight"]
    ordering = ["exercise__name", "series_number"]


class CardioSeriesLogInline(admin.TabularInline):
    model = CardioSeriesLog
    extra = 1
    fields = ["exercise", "series_number", "duration_seconds", "distance_m"]
    ordering = ["exercise__name", "series_number"]


class OneExerciceInline(admin.TabularInline):
    model = OneExercice
    extra = 1
    fields = ["position", "name"]
    ordering = ["position"]


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ["date", "type_workout", "duration", "get_exercise_count"]
    search_fields = ["date", "type_workout__name_workout"]
    list_filter = ["date", "type_workout", "duration"]
    fieldsets = ((None, {"fields": ("date", "type_workout", "duration")}),)
    inlines = [OneExerciceInline, StrengthSeriesLogInline, CardioSeriesLogInline]

    @admin.display(description="Exercises")
    def get_exercise_count(self, obj):
        strength_count = obj.strength_series_logs.count()
        cardio_count = obj.cardio_series_logs.count()
        total = strength_count + cardio_count
        return f"{total} ({strength_count}S, {cardio_count}C)"
