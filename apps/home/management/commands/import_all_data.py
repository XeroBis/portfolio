import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from apps.home.models import Tag, Projet, Testimonial
from apps.workout.models import TypeWorkout, Workout, Exercice, StrengthExerciseLog, CardioExerciseLog, OneExercice


class Command(BaseCommand):
    help = 'Import all data from data.json into Django models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data.json',
            help='Path to the JSON file to import (default: data.json)'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File {file_path} does not exist')
            )
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {e}')
            )
            return

        self.import_tags(data.get('tags', []))
        self.import_projects(data.get('projects', []))
        self.import_testimonials(data.get('testimonials', []))
        self.import_type_workouts(data.get('type_workouts', []))
        self.import_workouts(data.get('workouts', []))
        self.import_exercises(data.get('exercises', []))
        self.import_strength_exercise_logs(data.get('strength_exercise_logs', []))
        self.import_cardio_exercise_logs(data.get('cardio_exercise_logs', []))
        self.import_one_exercises(data.get('one_exercises', []))

        # Fix PostgreSQL sequences after import
        self.fix_sequences()

        self.stdout.write(
            self.style.SUCCESS('Successfully imported all data')
        )

    def import_tags(self, tags_data):
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                id=tag_data['id'],
                defaults={'name': tag_data['name']}
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
            else:
                self.stdout.write(f'Tag already exists: {tag.name}')

    def import_projects(self, projects_data):
        for project_data in projects_data:
            project, created = Projet.objects.get_or_create(
                title_en=project_data['title_en'],
                defaults={
                    'description_en': project_data['description_en'],
                    'title_fr': project_data['title_fr'],
                    'description_fr': project_data['description_fr'],
                    'github_url': project_data['github_url']
                }
            )

            # Handle many-to-many relationships
            for tag_id in project_data.get('tags', []):
                try:
                    tag = Tag.objects.get(id=tag_id)
                    project.tags.add(tag)
                except Tag.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Tag with id {tag_id} does not exist')
                    )

            if created:
                self.stdout.write(f'Created project: {project.title_en}')
            else:
                self.stdout.write(f'Project already exists: {project.title_en}')

    def import_testimonials(self, testimonials_data):
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                id=testimonial_data['id'],
                defaults={
                    'author': testimonial_data['author'],
                    'text_en': testimonial_data['text_en'],
                    'text_fr': testimonial_data['text_fr']
                }
            )
            if created:
                self.stdout.write(f'Created testimonial by: {testimonial.author}')
            else:
                self.stdout.write(f'Testimonial already exists by: {testimonial.author}')

    def import_type_workouts(self, type_workouts_data):
        for type_workout_data in type_workouts_data:
            type_workout, created = TypeWorkout.objects.get_or_create(
                id=type_workout_data['id'],
                defaults={'name_workout': type_workout_data['name_workout']}
            )
            if created:
                self.stdout.write(f'Created workout type: {type_workout.name_workout}')
            else:
                self.stdout.write(f'Workout type already exists: {type_workout.name_workout}')

    def import_workouts(self, workouts_data):
        for workout_data in workouts_data:
            try:
                type_workout = TypeWorkout.objects.get(id=workout_data['type_workout'])
            except TypeWorkout.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'TypeWorkout with id {workout_data["type_workout"]} does not exist')
                )
                type_workout = None

            workout, created = Workout.objects.get_or_create(
                id=workout_data['id'],
                defaults={
                    'date': datetime.strptime(workout_data['date'], '%Y-%m-%d').date(),
                    'type_workout': type_workout,
                    'duration': workout_data['duration']
                }
            )
            if created:
                self.stdout.write(f'Created workout: {workout}')
            else:
                self.stdout.write(f'Workout already exists: {workout}')

    def import_exercises(self, exercises_data):
        for exercise_data in exercises_data:
            exercise, created = Exercice.objects.get_or_create(
                id=exercise_data['id'],
                defaults={
                    'name': exercise_data['name'],
                    'exercise_type': exercise_data['exercise_type']
                }
            )
            if created:
                self.stdout.write(f'Created exercise: {exercise.name}')
            else:
                self.stdout.write(f'Exercise already exists: {exercise.name}')

    def import_strength_exercise_logs(self, strength_logs_data):
        for log_data in strength_logs_data:
            try:
                exercise = Exercice.objects.get(id=log_data['exercise_id'])
                workout = Workout.objects.get(id=log_data['workout_id'])
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Missing exercise or workout: {e}')
                )
                continue

            log, created = StrengthExerciseLog.objects.get_or_create(
                id=log_data['id'],
                defaults={
                    'exercise': exercise,
                    'workout': workout,
                    'nb_series': log_data['nb_series'],
                    'nb_repetition': log_data['nb_repetition'],
                    'weight': log_data['weight'],
                    'notes': log_data['notes']
                }
            )
            if created:
                self.stdout.write(f'Created strength log: {log}')
            else:
                self.stdout.write(f'Strength log already exists: {log}')

    def import_cardio_exercise_logs(self, cardio_logs_data):
        for log_data in cardio_logs_data:
            try:
                exercise = Exercice.objects.get(id=log_data['exercise_id'])
                workout = Workout.objects.get(id=log_data['workout_id'])
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Missing exercise or workout: {e}')
                )
                continue

            log, created = CardioExerciseLog.objects.get_or_create(
                id=log_data['id'],
                defaults={
                    'exercise': exercise,
                    'workout': workout,
                    'duration_seconds': log_data['duration_seconds'],
                    'distance_m': log_data['distance_m'],
                    'notes': log_data['notes']
                }
            )
            if created:
                self.stdout.write(f'Created cardio log: {log}')
            else:
                self.stdout.write(f'Cardio log already exists: {log}')

    def import_one_exercises(self, one_exercises_data):
        for one_exercise_data in one_exercises_data:
            try:
                exercise = Exercice.objects.get(id=one_exercise_data['name_id'])
                workout = Workout.objects.get(id=one_exercise_data['seance_id'])

                # Handle both old format (content_type_id) and new format (app_label + model)
                if 'content_type_id' in one_exercise_data:
                    content_type = ContentType.objects.get(id=one_exercise_data['content_type_id'])
                else:
                    app_label = one_exercise_data['content_type_app_label']
                    model = one_exercise_data['content_type_model']
                    if app_label and model:
                        content_type = ContentType.objects.get(app_label=app_label, model=model)
                    else:
                        content_type = None

            except (Exercice.DoesNotExist, Workout.DoesNotExist, ContentType.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Missing reference for OneExercice: {e}')
                )
                continue

            one_exercise, created = OneExercice.objects.get_or_create(
                id=one_exercise_data['id'],
                defaults={
                    'name': exercise,
                    'seance': workout,
                    'content_type': content_type,
                    'object_id': one_exercise_data['object_id']
                }
            )
            if created:
                self.stdout.write(f'Created OneExercice: {one_exercise}')
            else:
                self.stdout.write(f'OneExercice already exists: {one_exercise}')

    def fix_sequences(self):
        """Fix PostgreSQL sequences after importing data with explicit IDs"""
        self.stdout.write('Fixing PostgreSQL sequences...')

        sql_commands = [
            # Home app sequences
            "SELECT setval(pg_get_serial_sequence('\"home_tag\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"home_tag\";",
            "SELECT setval(pg_get_serial_sequence('\"home_projet\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"home_projet\";",
            "SELECT setval(pg_get_serial_sequence('\"home_testimonial\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"home_testimonial\";",
            # Workout app sequences
            "SELECT setval(pg_get_serial_sequence('\"workout_typeworkout\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_typeworkout\";",
            "SELECT setval(pg_get_serial_sequence('\"workout_workout\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_workout\";",
            "SELECT setval(pg_get_serial_sequence('\"workout_exercice\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_exercice\";",
            "SELECT setval(pg_get_serial_sequence('\"workout_strengthexerciselog\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_strengthexerciselog\";",
            "SELECT setval(pg_get_serial_sequence('\"workout_cardioexerciselog\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_cardioexerciselog\";",
            "SELECT setval(pg_get_serial_sequence('\"workout_oneexercice\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"workout_oneexercice\";"
        ]

        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if result:
                        table_name = sql.split('"')[1]
                        self.stdout.write(f'Fixed sequence for {table_name}: next ID will be {result[0] + 1}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Could not fix sequence: {sql} - Error: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully fixed all sequences!')
        )