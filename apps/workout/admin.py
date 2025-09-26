from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import (
    TypeWorkout, Workout, Exercice, OneExercice,
    StrengthExerciseLog, CardioExerciseLog
)


class OneExerciceForm(forms.ModelForm):
    nb_series = forms.IntegerField(required=False, label='Series')
    nb_repetition = forms.IntegerField(required=False, label='Reps')
    weight = forms.IntegerField(required=False, label='Weight (kg)')
    duration_seconds = forms.IntegerField(required=False, label='Duration (s)')
    distance_m = forms.FloatField(required=False, label='Distance (m)')
    exercise_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label='Notes')

    class Meta:
        model = OneExercice
        fields = ['position', 'name', 'nb_series', 'nb_repetition', 'weight', 'duration_seconds', 'distance_m', 'exercise_notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.exercise_log:
            log = self.instance.exercise_log
            if hasattr(log, 'nb_series'):
                self.fields['nb_series'].initial = log.nb_series
                self.fields['nb_repetition'].initial = log.nb_repetition
                self.fields['weight'].initial = log.weight
            elif hasattr(log, 'duration_seconds'):
                self.fields['duration_seconds'].initial = log.duration_seconds
                self.fields['distance_m'].initial = log.distance_m
            if hasattr(log, 'notes'):
                self.fields['exercise_notes'].initial = log.notes

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Handle exercise log creation/update
            exercise_type = instance.name.exercise_type if instance.name else 'strength'

            # Get or create the appropriate exercise log
            if exercise_type == 'strength':
                if instance.exercise_log and isinstance(instance.exercise_log, StrengthExerciseLog):
                    log = instance.exercise_log
                else:
                    log = StrengthExerciseLog.objects.create(
                        exercise=instance.name,
                        workout=instance.seance,
                        nb_series=self.cleaned_data.get('nb_series', 1),
                        nb_repetition=self.cleaned_data.get('nb_repetition', 1),
                        weight=self.cleaned_data.get('weight', 0)
                    )
                    instance.content_type = ContentType.objects.get_for_model(StrengthExerciseLog)
                    instance.object_id = log.pk
                    instance.exercise_log = log

                log.nb_series = self.cleaned_data.get('nb_series', log.nb_series)
                log.nb_repetition = self.cleaned_data.get('nb_repetition', log.nb_repetition)
                log.weight = self.cleaned_data.get('weight', log.weight)
                log.notes = self.cleaned_data.get('exercise_notes', '')
                log.save()

            elif exercise_type == 'cardio':
                if instance.exercise_log and isinstance(instance.exercise_log, CardioExerciseLog):
                    log = instance.exercise_log
                else:
                    log = CardioExerciseLog.objects.create(
                        exercise=instance.name,
                        workout=instance.seance,
                        duration_seconds=self.cleaned_data.get('duration_seconds', 0),
                        distance_m=self.cleaned_data.get('distance_m', None)
                    )
                    instance.content_type = ContentType.objects.get_for_model(CardioExerciseLog)
                    instance.object_id = log.pk
                    instance.exercise_log = log

                log.duration_seconds = self.cleaned_data.get('duration_seconds', log.duration_seconds)
                log.distance_m = self.cleaned_data.get('distance_m', log.distance_m)
                log.notes = self.cleaned_data.get('exercise_notes', '')
                log.save()

            instance.save()

        return instance


@admin.register(TypeWorkout)
class TypeWorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_workout')
    search_fields = ('name_workout',)
    ordering = ('name_workout',)


class OneExerciceInline(admin.TabularInline):
    model = OneExercice
    form = OneExerciceForm
    extra = 0
    fields = ('position', 'name', 'nb_series', 'nb_repetition', 'weight', 'duration_seconds', 'distance_m', 'exercise_notes')
    ordering = ('position',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('name', 'content_type').prefetch_related('exercise_log')


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'type_workout', 'duration_minutes')
    list_filter = ('date', 'type_workout')
    search_fields = ('date', 'type_workout__name_workout')
    date_hierarchy = 'date'
    ordering = ('-date',)
    inlines = [OneExerciceInline]

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
    list_display = ('id', 'name', 'seance', 'position', 'seance_date', 'exercise_details')
    list_filter = ('seance__date', 'name__exercise_type')
    search_fields = ('name__name', 'seance__date')
    raw_id_fields = ('name', 'seance')
    ordering = ('-seance__date', 'position')

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
