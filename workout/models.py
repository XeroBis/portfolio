from django.db import models


class TypeWorkout(models.Model):
    name_workout_fr = models.CharField(max_length=50)
    name_workout_en = models.CharField(max_length=50, default="Workout")

    def __str__(self):
        return self.name_workout_fr


class Workout(models.Model):
    date = models.DateField()
    type_workout = models.ForeignKey(TypeWorkout, null=True, on_delete=models.SET_NULL)
    duration = models.IntegerField(default=0)

    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d')
        type_workout_name = self.type_workout.name_workout_fr if self.type_workout else "No Type"

        return f"{date_str} - {type_workout_name}"


class Exercice(models.Model):
    """
    Exercice global
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class OneExercice(models.Model):

    name = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    seance = models.ForeignKey(Workout, on_delete=models.CASCADE)
    nb_series = models.IntegerField()
    nb_repetition = models.IntegerField()
    weight = models.IntegerField()

    def __str__(self):
        exercice_name = self.name.name if self.name else "No Exercice"
        seance_date = self.seance.date.strftime('%Y-%m-%d') if self.seance else "No Seance"
        
        return f"{exercice_name} - {seance_date}"