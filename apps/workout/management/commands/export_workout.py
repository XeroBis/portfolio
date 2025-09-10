import csv
from django.core.management.base import BaseCommand
from apps.workout.models import OneExercice
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Export workout data to a CSV file'

    def handle(self, *args, **kwargs):

        
        today_date = datetime.today().strftime('%Y-%m-%d')
        is_prod = "PROD" if os.getenv('IS_PROD', False) == 'True' else "LOCAL"

        csv_file_path = f'data/{is_prod}/workout_{is_prod}_{today_date}.csv'
        with open(csv_file_path, mode='w', newline='') as csvfile:

            fieldnames = ['time', 'type', 'id_exercice', 'nb_series', 'nb_repetition', 'weight']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            one_exercices = OneExercice.objects.all()

            for one_exercice in one_exercices:
                date = one_exercice.seance.date
                workout_type_name = one_exercice.seance.type_workout.name
                exercice_id = one_exercice.name.id
                nb_series = one_exercice.nb_series
                nb_repetition = one_exercice.nb_repetition
                weight = one_exercice.weight

                writer.writerow({
                    'time': date.strftime('%Y-%m-%d'),
                    'type': workout_type_name,
                    'id_exercice': exercice_id,
                    'nb_series': nb_series,
                    'nb_repetition': nb_repetition,
                    'weight': weight,
                })

        self.stdout.write(self.style.SUCCESS('Workout data exported successfully!'))
