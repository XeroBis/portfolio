import csv
from django.core.management.base import BaseCommand
from home.models import Exercice

class Command(BaseCommand):
    help = 'Import exercises from a CSV file'

    def handle(self, *args, **kwargs):

        csv_file_path = 'exercises.csv' # à changer

        with open(csv_file_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                exercise_id = row['id_exercice']
                name_exercice = row['name_exercice']
                exercise, created = Exercice.objects.update_or_create(
                    id=exercise_id,
                    defaults={'name': name_exercice}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Exercise "{name_exercice}" created successfully!'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Exercise "{name_exercice}" updated successfully!'))

        self.stdout.write(self.style.SUCCESS('Exercises imported successfully!'))
