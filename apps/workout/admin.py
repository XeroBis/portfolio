from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import (
    CardioExerciseLog,
    Equipment,
    Exercice,
    MuscleGroup,
    OneExercice,
    StrengthExerciseLog,
    TypeWorkout,
    Workout,
)


class OneExerciceForm(forms.ModelForm):
    nb_series = forms.IntegerField(required=False, label="Series")
    nb_repetition = forms.IntegerField(required=False, label="Reps")
    weight = forms.IntegerField(required=False, label="Weight (kg)")
    duration_seconds = forms.IntegerField(required=False, label="Duration (s)")
    distance_m = forms.FloatField(required=False, label="Distance (m)")
    exercise_notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}), label="Notes"
    )

    class Meta:
        model = OneExercice
        fields = [
            "position",
            "name",
            "nb_series",
            "nb_repetition",
            "weight",
            "duration_seconds",
            "distance_m",
            "exercise_notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine exercise type
        exercise_type = None
        if self.instance and self.instance.pk and self.instance.name:
            exercise_type = self.instance.name.exercise_type

        # Hide fields based on exercise type
        if exercise_type == "strength":
            # Hide cardio fields
            self.fields["duration_seconds"].widget = forms.HiddenInput()
            self.fields["distance_m"].widget = forms.HiddenInput()
        elif exercise_type == "cardio":
            # Hide strength fields
            self.fields["nb_series"].widget = forms.HiddenInput()
            self.fields["nb_repetition"].widget = forms.HiddenInput()
            self.fields["weight"].widget = forms.HiddenInput()

        # Populate initial values from existing log
        if self.instance and self.instance.pk and self.instance.exercise_log:
            log = self.instance.exercise_log
            if hasattr(log, "nb_series"):
                self.fields["nb_series"].initial = log.nb_series
                self.fields["nb_repetition"].initial = log.nb_repetition
                self.fields["weight"].initial = log.weight
            elif hasattr(log, "duration_seconds"):
                self.fields["duration_seconds"].initial = log.duration_seconds
                self.fields["distance_m"].initial = log.distance_m
            if hasattr(log, "notes"):
                self.fields["exercise_notes"].initial = log.notes

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Handle exercise log creation/update
            exercise_type = instance.name.exercise_type if instance.name else "strength"

            # Get or create the appropriate exercise log
            if exercise_type == "strength":
                if instance.exercise_log and isinstance(
                    instance.exercise_log, StrengthExerciseLog
                ):
                    log = instance.exercise_log
                else:
                    log = StrengthExerciseLog.objects.create(
                        exercise=instance.name,
                        workout=instance.seance,
                        nb_series=self.cleaned_data.get("nb_series", 1),
                        nb_repetition=self.cleaned_data.get("nb_repetition", 1),
                        weight=self.cleaned_data.get("weight", 0),
                    )
                    instance.content_type = ContentType.objects.get_for_model(
                        StrengthExerciseLog
                    )
                    instance.object_id = log.pk
                    instance.exercise_log = log

                log.nb_series = self.cleaned_data.get("nb_series", log.nb_series)
                log.nb_repetition = self.cleaned_data.get(
                    "nb_repetition", log.nb_repetition
                )
                log.weight = self.cleaned_data.get("weight", log.weight)
                log.notes = self.cleaned_data.get("exercise_notes", "")
                log.save()

            elif exercise_type == "cardio":
                if instance.exercise_log and isinstance(
                    instance.exercise_log, CardioExerciseLog
                ):
                    log = instance.exercise_log
                else:
                    log = CardioExerciseLog.objects.create(
                        exercise=instance.name,
                        workout=instance.seance,
                        duration_seconds=self.cleaned_data.get("duration_seconds", 0),
                        distance_m=self.cleaned_data.get("distance_m", None),
                    )
                    instance.content_type = ContentType.objects.get_for_model(
                        CardioExerciseLog
                    )
                    instance.object_id = log.pk
                    instance.exercise_log = log

                log.duration_seconds = self.cleaned_data.get(
                    "duration_seconds", log.duration_seconds
                )
                log.distance_m = self.cleaned_data.get("distance_m", log.distance_m)
                log.notes = self.cleaned_data.get("exercise_notes", "")
                log.save()

            instance.save()

        return instance


@admin.register(TypeWorkout)
class TypeWorkoutAdmin(admin.ModelAdmin):
    list_display = ("id", "name_workout")
    search_fields = ("name_workout",)
    ordering = ("name_workout",)


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")
    ordering = ("name",)


class OneExerciceInline(admin.TabularInline):
    model = OneExercice
    form = OneExerciceForm
    extra = 0
    fields = (
        "position",
        "name",
        "nb_series",
        "nb_repetition",
        "weight",
        "duration_seconds",
        "distance_m",
        "exercise_notes",
    )
    ordering = ("position",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("name", "content_type")
            .prefetch_related("exercise_log")
        )


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "type_workout", "duration_minutes")
    list_filter = ("date", "type_workout")
    search_fields = ("date", "type_workout__name_workout")
    date_hierarchy = "date"
    ordering = ("-date",)
    inlines = [OneExerciceInline]

    @admin.display(description="Duration")
    def duration_minutes(self, obj):
        return f"{obj.duration} min"


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "exercise_type",
        "difficulty",
        "display_muscle_groups",
        "display_equipment",
    )
    list_filter = ("exercise_type", "difficulty", "muscle_groups", "equipment")
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("muscle_groups", "equipment")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "exercise_type")}),
        ("Exercise Details", {"fields": ("muscle_groups", "difficulty", "equipment")}),
    )

    @admin.display(description="Muscle Groups")
    def display_muscle_groups(self, obj):
        return (
            ", ".join([mg.name for mg in obj.muscle_groups.all()[:3]])
            if obj.muscle_groups.exists()
            else "-"
        )

    @admin.display(description="Equipment")
    def display_equipment(self, obj):
        return (
            ", ".join([eq.name for eq in obj.equipment.all()[:3]])
            if obj.equipment.exists()
            else "-"
        )


@admin.register(OneExercice)
class OneExerciceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "seance",
        "position",
        "seance_date",
        "exercise_details",
    )
    list_filter = ("seance__date", "name__exercise_type")
    search_fields = ("name__name", "seance__date")
    raw_id_fields = ("name", "seance")
    ordering = ("-seance__date", "position")
    form = OneExerciceForm
    fieldsets = (
        ("Exercise Information", {"fields": ("seance", "name", "position")}),
        (
            "Exercise Details",
            {
                "fields": (
                    "nb_series",
                    "nb_repetition",
                    "weight",
                    "duration_seconds",
                    "distance_m",
                    "exercise_notes",
                ),
            },
        ),
    )

    @admin.display(description="Workout Date")
    def seance_date(self, obj):
        return obj.seance.date if obj.seance else "No Date"

    @admin.display(description="Details")
    def exercise_details(self, obj):
        if obj.exercise_log:
            if hasattr(obj.exercise_log, "nb_series"):
                series = obj.exercise_log.nb_series
                reps = obj.exercise_log.nb_repetition
                weight = obj.exercise_log.weight
                return f"{series}x{reps} @ {weight}kg"
            elif hasattr(obj.exercise_log, "duration_seconds"):
                distance = (
                    f" - {obj.exercise_log.distance_m}m"
                    if obj.exercise_log.distance_m
                    else ""
                )
                return f"{obj.exercise_log.duration_seconds}s{distance}"
        return "No details"
