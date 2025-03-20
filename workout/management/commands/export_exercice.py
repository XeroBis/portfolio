import csv
from django.core.management.base import BaseCommand
from workout.models import Exercice
from datetime import datetime
import os


class Command(BaseCommand):
    help = 'Export all exercises to a CSV file'

    def handle(self, *args, **kwargs):
        
        today_date = datetime.today().strftime('%Y-%m-%d')
        is_prod = "PROD" if os.getenv('IS_PROD', False) == 'True' else "LOCAL"

        csv_file_path = f'data/{is_prod}/exercises_{is_prod}_{today_date}.csv'
        with open(csv_file_path, mode='w', newline='') as csvfile:
            fieldnames = ['id_exercice', 'name_exercice']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            exercises = Exercice.objects.all()

            for exercise in exercises:
                writer.writerow({
                    'id_exercice': exercise.id,
                    'name_exercice': exercise.name,
                })

        self.stdout.write(self.style.SUCCESS('Exercises exported successfully!'))
