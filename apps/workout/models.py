from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class TypeWorkout(models.Model):
    name_workout = models.CharField(max_length=50)

    def __str__(self):
        return self.name_workout


class Workout(models.Model):
    date = models.DateField()
    type_workout = models.ForeignKey(TypeWorkout, null=True, on_delete=models.SET_NULL)
    duration = models.IntegerField(default=0)

    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d')
        type_workout_name = self.type_workout.name_workout if self.type_workout else "No Type"

        return f"{date_str} - {type_workout_name}"


class Exercice(models.Model):
    """
    Exercice global
    """
    name = models.CharField(max_length=50)
    exercise_type = models.CharField(max_length=20, choices=[
        ('strength', 'Strength'),
        ('cardio', 'Cardio')
    ], default='strength')

    def __str__(self):
        return self.name


class BaseExerciseLog(models.Model):
    """
    Abstract base class for exercise logs
    """
    exercise = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True

    def get_display_data(self):
        """Override in subclasses to return exercise-specific display data"""
        raise NotImplementedError


class StrengthExerciseLog(BaseExerciseLog):
    nb_series = models.IntegerField()
    nb_repetition = models.IntegerField()
    weight = models.IntegerField()

    def get_display_data(self):
        return {
            'type': 'strength',
            'nb_series': self.nb_series,
            'nb_repetition': self.nb_repetition,
            'weight': self.weight,
        }

    def __str__(self):
        return f"{self.exercise.name} - {self.nb_series}x{self.nb_repetition} @ {self.weight}kg"


class CardioExerciseLog(BaseExerciseLog):
    duration_seconds = models.IntegerField(null=True, blank=True)
    distance_m = models.FloatField(null=True, blank=True)

    def get_display_data(self):
        return {
            'type': 'cardio',
            'duration_seconds': self.duration_seconds,
            'distance_m': self.distance_m
        }

    def __str__(self):
        distance_str = f" - {self.distance_m}m" if self.distance_m else ""
        return f"{self.exercise.name} - {self.duration_seconds}min{distance_str}"


class OneExercice(models.Model):
    """
    Polymorphic exercise log using generic foreign key
    """
    name = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    seance = models.ForeignKey(Workout, on_delete=models.CASCADE)

    # Generic foreign key to point to specific exercise log
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    exercise_log = GenericForeignKey('content_type', 'object_id')

    def get_display_data(self):
        """Get display data from the specific exercise log"""
        if self.exercise_log:
            return self.exercise_log.get_display_data()
        return {}

    def __str__(self):
        exercice_name = self.name.name if self.name else "No Exercice"
        seance_date = self.seance.date.strftime('%Y-%m-%d') if self.seance else "No Seance"

        return f"{exercice_name} - {seance_date}"