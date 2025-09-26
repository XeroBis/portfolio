import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
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

        self.stdout.write(
            self.style.SUCCESS('Successfully imported all data')
        )

    def import_tags(self, tags_data):
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name']
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
            for tag_name in project_data.get('tag_names', []):
                try:
                    tag = Tag.objects.get(name=tag_name)
                    project.tags.add(tag)
                except Tag.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Tag with name "{tag_name}" does not exist')
                    )

            if created:
                self.stdout.write(f'Created project: {project.title_en}')
            else:
                self.stdout.write(f'Project already exists: {project.title_en}')

    def import_testimonials(self, testimonials_data):
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                author=testimonial_data['author'],
                defaults={
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
                name_workout=type_workout_data['name_workout']
            )
            if created:
                self.stdout.write(f'Created workout type: {type_workout.name_workout}')
            else:
                self.stdout.write(f'Workout type already exists: {type_workout.name_workout}')

    def import_workouts(self, workouts_data):
        for workout_data in workouts_data:
            try:
                type_workout = TypeWorkout.objects.get(name_workout=workout_data['type_workout_name'])
            except TypeWorkout.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'TypeWorkout with name "{workout_data["type_workout_name"]}" does not exist')
                )
                type_workout = None

            workout, created = Workout.objects.get_or_create(
                date=datetime.strptime(workout_data['date'], '%Y-%m-%d').date(),
                type_workout=type_workout,
                defaults={
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
                name=exercise_data['name'],
                defaults={
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
                exercise = Exercice.objects.get(name=log_data['exercise_name'])
                workout_date = datetime.strptime(log_data['workout_date'], '%Y-%m-%d').date()
                workout = Workout.objects.get(date=workout_date)
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Missing exercise or workout: {e}')
                )
                continue

            log, created = StrengthExerciseLog.objects.get_or_create(
                exercise=exercise,
                workout=workout,
                defaults={
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
                exercise = Exercice.objects.get(name=log_data['exercise_name'])
                workout_date = datetime.strptime(log_data['workout_date'], '%Y-%m-%d').date()
                workout = Workout.objects.get(date=workout_date)
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Missing exercise or workout: {e}')
                )
                continue

            log, created = CardioExerciseLog.objects.get_or_create(
                exercise=exercise,
                workout=workout,
                defaults={
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
                exercise = Exercice.objects.get(name=one_exercise_data['exercise_name'])
                workout_date = datetime.strptime(one_exercise_data['workout_date'], '%Y-%m-%d').date()
                workout = Workout.objects.get(date=workout_date)

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
                name=exercise,
                seance=workout,
                defaults={
                    'content_type': content_type,
                    'object_id': one_exercise_data['object_id']
                }
            )
            if created:
                self.stdout.write(f'Created OneExercice: {one_exercise}')
            else:
                self.stdout.write(f'OneExercice already exists: {one_exercise}')