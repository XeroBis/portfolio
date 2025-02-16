import csv
from django.core.management.base import BaseCommand
from home.models import TypeWorkout, Workout, Exercice, OneExercice

class Command(BaseCommand):
    help = 'Export workout data to a CSV file'

    def handle(self, *args, **kwargs):
        # Path to your CSV file
        csv_file_path = 'workouts_export.csv'

        # Open the CSV file for writing
        with open(csv_file_path, mode='w', newline='') as csvfile:
            fieldnames = ['time', 'type', 'id_exercice', 'nb_series', 'nb_repetition', 'weight']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header
            writer.writeheader()

            # Query all OneExercice objects
            one_exercices = OneExercice.objects.all()

            for one_exercice in one_exercices:
                # Extract data from the OneExercice object
                date = one_exercice.seance.date
                workout_type_name = one_exercice.seance.type_workout.name
                exercice_id = self.get_exercise_id(one_exercice.name.name)
                nb_series = one_exercice.nb_series
                nb_repetition = one_exercice.nb_repetition
                weight = one_exercice.weight

                # Write the row to the CSV file
                writer.writerow({
                    'time': date.strftime('%Y-%m-%d'),
                    'type': workout_type_name,
                    'id_exercice': exercice_id,
                    'nb_series': nb_series,
                    'nb_repetition': nb_repetition,
                    'weight': weight,
                })

        self.stdout.write(self.style.SUCCESS('Workout data exported successfully!'))

    def get_exercise_id(self, exercise_name):
        exercises = {
            "90/90": 0,
            "Split squat": 1,
            "Cossak squat": 2,
            "Deep squat into harmstring stretch": 3,
            "Thoracic twist": 4,
            "Cat cow": 5,
            "Child pose into seal pose": 6,
            "Kickbacks": 7,
            "Leg raises": 8,
            "V-sit": 9,
            "Russian twist": 10,
            "Bicycle crunch": 11,
            "Bench press": 12,
            "Dumbbell shoulder": 13,
            "Dumbbell incline chest": 14,
            "Dumbbell side lateral": 15,
            "Dumbbell skull crusher": 16,
            "Standing overhead dumbbell": 17,
            "Push-ups": 18,
            "Bent over row": 19,
            "Dumbbell pullover": 20,
            "Barbell overhead press": 21,
            "Dips": 22,
            "Bent over row": 24,
            "Standing Barbell": 26,
            "Dumbbell row unilateral": 27,
            "Barbell curl": 28,
            "Dumbbell hammer curl": 29,
            "Rowing Barbell": 30,
            "Elastic pull": 31,
            "Pull over barbell": 32,
            "Curl elastic": 33,
            "Face pull": 34,
            "Squat": 35,
            "Romanian dead lift": 36,
            "Seated leg curl": 38,
            "Calf raises": 39,
        }
        return exercises.get(exercise_name, -1)  # Return -1 if exercise name is not found&