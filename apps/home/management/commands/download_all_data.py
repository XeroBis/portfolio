import json
from django.core.management.base import BaseCommand
from apps.home.models import Tag, Projet, Testimonial
from apps.workout.models import (
    TypeWorkout, Workout, Exercice, OneExercice,
    StrengthExerciseLog, CardioExerciseLog
)


class Command(BaseCommand):
    help = 'Download all data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data.json',
            help='Path to the JSON file (default: data.json)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        self.download_data(file_path)

    def download_data(self, file_path):
        self.stdout.write('Starting data export...')

        data = {
            "tags": list(Tag.objects.values()),
            "projects": [
                {
                    "id": proj.id,
                    "title_en": proj.title_en,
                    "description_en": proj.description_en,
                    "title_fr": proj.title_fr,
                    "description_fr": proj.description_fr,
                    "github_url": proj.github_url,
                    "tags": list(proj.tags.values_list("id", flat=True))
                }
                for proj in Projet.objects.all()
            ],
            "testimonials": list(Testimonial.objects.values()),
            "type_workouts": list(TypeWorkout.objects.values()),
            "workouts": [
                {
                    "id": workout.id,
                    "date": workout.date.strftime("%Y-%m-%d"),
                    "type_workout": workout.type_workout_id,
                    "duration": workout.duration
                }
                for workout in Workout.objects.all()
            ],
            "exercises": list(Exercice.objects.values()),
            "strength_exercise_logs": [
                {
                    "id": log.id,
                    "exercise_id": log.exercise_id,
                    "workout_id": log.workout_id,
                    "nb_series": log.nb_series,
                    "nb_repetition": log.nb_repetition,
                    "weight": log.weight,
                    "notes": log.notes
                }
                for log in StrengthExerciseLog.objects.all()
            ],
            "cardio_exercise_logs": [
                {
                    "id": log.id,
                    "exercise_id": log.exercise_id,
                    "workout_id": log.workout_id,
                    "duration_seconds": log.duration_seconds,
                    "distance_m": log.distance_m,
                    "notes": log.notes
                }
                for log in CardioExerciseLog.objects.all()
            ],
            "one_exercises": [
                {
                    "id": one_ex.id,
                    "name_id": one_ex.name_id,
                    "seance_id": one_ex.seance_id,
                    "content_type_app_label": one_ex.content_type.app_label if one_ex.content_type else None,
                    "content_type_model": one_ex.content_type.model if one_ex.content_type else None,
                    "object_id": one_ex.object_id
                }
                for one_ex in OneExercice.objects.all()
            ]
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.stdout.write(
                self.style.SUCCESS(f'Data successfully exported to {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error exporting data: {e}')
            )