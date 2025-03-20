import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from workout.models import TypeWorkout, Workout, Exercice, OneExercice

class Command(BaseCommand):
    help = 'Import workout data from a CSV file into the database'

    def handle(self, *args, **kwargs):

        csv_file_path = 'data/PROD/workout_PROD_2025-03-20.csv' # à changer

        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                date = timezone.datetime.strptime(row['time'], '%Y-%m-%d').date()
                workout_type_name = row['type']
                exercice_id = int(row['id_exercice'])
                nb_series = int(row['nb_series'])
                nb_repetition = int(row['nb_repetition'])
                weight = int(row['weight'])

                type_workout, _ = TypeWorkout.objects.get_or_create(name=workout_type_name)
                workout, _ = Workout.objects.get_or_create(date=date, type_workout=type_workout)

                try:
                    exercice = Exercice.objects.get(id=exercice_id)
                except Exercice.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Exercice with ID {exercice_id} does not exist."))
                    continue

                OneExercice.objects.create(
                    name=exercice,
                    seance=workout,
                    nb_series=nb_series,
                    nb_repetition=nb_repetition,
                    weight=weight,
                )

        self.stdout.write(self.style.SUCCESS('Workout data imported successfully!'))
