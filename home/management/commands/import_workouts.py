import csv
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import TypeWorkout, Workout, Exercice, OneExercice

def get_exercise_name(exercise_id):
    exercises = {
        0: "90/90",
        1: "Split squat",
        2: "Cossak squat",
        3: "Deep squat into harmstring stretch",
        4: "Thoracic twist",
        5: "Cat cow",
        6: "Child pose into seal pose",
        7: "Kickbacks",
        8: "Leg raises",
        9: "V-sit",
        10: "Russian twist",
        11: "Bicycle crunch",
        12: "Bench press",
        13: "Dumbbell shoulder",
        14: "Dumbbell incline chest",
        15: "Dumbbell side lateral",
        16: "Dumbbell skull crusher",
        17: "Standing overhead dumbbell",
        18: "Push-ups",
        19: "Bent over row",
        20: "Dumbbell pullover",
        21: "Barbell overhead press",
        22: "Dips",
        24: "Bent over row",
        26: "Standing Barbell",
        27: "Dumbbell row unilateral",
        28:"Barbell curl",
        29:"Dumbbell hammer curl",
        30:"Rowing Barbell",
        31:"Elastic pull",
        32:"Pull over barbell",
        33:"Curl elastic",
        34:"Face pull",
        35:"Squat",
        36:"Romanian dead lift",
        38:"Seated leg curl",
        39:"Calf raises",
    }
    return exercises.get(exercise_id, "Exercice introuvable")

class Command(BaseCommand):
    help = 'Import workout data from a CSV file into the database'

    def handle(self, *args, **kwargs):
        # Path to your CSV file
        csv_file_path = 'workouts.csv'

        # Open the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract data from the row
                date = timezone.datetime.strptime(row['time'], '%Y-%m-%d').date()
                workout_type_name = row['type']
                exercice_id = int(row['id_exercice'])
                nb_series = int(row['nb_series'])
                nb_repetition = int(row['nb_repetition'])
                weight = int(row['weight'])

                # Get or create the TypeWorkout
                type_workout, _ = TypeWorkout.objects.get_or_create(name=workout_type_name)

                # Get or create the Workout
                workout, _ = Workout.objects.get_or_create(date=date, type_workout=type_workout)

                # Get the Exercice
                name_exo = get_exercise_name(exercice_id)
                try:
                    exercice = Exercice.objects.get(name=get_exercise_name(exercice_id))
                except Exercice.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Exercice with name {name_exo} does not exist."))
                    continue

                # Create the OneExercice
                OneExercice.objects.create(
                    name=exercice,
                    seance=workout,
                    nb_series=nb_series,
                    nb_repetition=nb_repetition,
                    weight=weight,
                    time=timedelta(seconds=0)
                )

        self.stdout.write(self.style.SUCCESS('Workout data imported successfully!'))