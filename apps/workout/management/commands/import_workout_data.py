import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection

from apps.workout.models import (
    CardioExerciseLog,
    Equipment,
    Exercice,
    MuscleGroup,
    OneExercice,
    StrengthExerciseLog,
    TypeWorkout,
    Workout,
)


class Command(BaseCommand):
    help = "Import all workout data from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Input JSON file path",
        )

    def handle(self, *args, **kwargs):
        input_path = kwargs["file"]

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {input_path}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON file: {e}"))
            return

        self.stdout.write("Importing data...")

        self.import_type_workouts(data.get("type_workouts", []))
        self.import_muscle_groups(data.get("muscle_groups", []))
        self.import_equipment(data.get("equipment", []))
        self.import_exercises(data.get("exercises", []))
        self.import_workouts(data.get("workouts", []))
        self.import_strength_logs(data.get("strength_exercise_logs", []))
        self.import_cardio_logs(data.get("cardio_exercise_logs", []))
        self.import_one_exercises(data.get("one_exercises", []))

        self.fix_sequences()

        self.stdout.write(
            self.style.SUCCESS(
                f"All workout data imported successfully from {input_path}"
            )
        )

    def import_type_workouts(self, type_workouts):
        for tw_data in type_workouts:
            TypeWorkout.objects.update_or_create(
                id=tw_data["id"], defaults={"name_workout": tw_data["name_workout"]}
            )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(type_workouts)} type workouts")
        )

    def import_muscle_groups(self, muscle_groups):
        for mg_data in muscle_groups:
            MuscleGroup.objects.update_or_create(
                id=mg_data["id"],
                defaults={
                    "name": mg_data["name"],
                    "description": mg_data.get("description", ""),
                },
            )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(muscle_groups)} muscle groups")
        )

    def import_equipment(self, equipment_list):
        for eq_data in equipment_list:
            Equipment.objects.update_or_create(
                id=eq_data["id"],
                defaults={
                    "name": eq_data["name"],
                    "description": eq_data.get("description", ""),
                },
            )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(equipment_list)} equipment")
        )

    def import_exercises(self, exercises):
        for ex_data in exercises:
            exercise, created = Exercice.objects.update_or_create(
                id=ex_data["id"],
                defaults={
                    "name": ex_data["name"],
                    "exercise_type": ex_data["exercise_type"],
                    "difficulty": ex_data.get("difficulty", ""),
                },
            )

            if "muscle_groups" in ex_data:
                exercise.muscle_groups.set(ex_data["muscle_groups"])
            if "equipment" in ex_data:
                exercise.equipment.set(ex_data["equipment"])

        self.stdout.write(self.style.SUCCESS(f"  Imported {len(exercises)} exercises"))

    def import_workouts(self, workouts):
        for w_data in workouts:
            type_workout = None
            if w_data.get("type_workout_id"):
                try:
                    type_workout = TypeWorkout.objects.get(id=w_data["type_workout_id"])
                except TypeWorkout.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  TypeWorkout with id "
                            f"{w_data['type_workout_id']} not found"
                        )
                    )

            Workout.objects.update_or_create(
                id=w_data["id"],
                defaults={
                    "date": datetime.strptime(w_data["date"], "%Y-%m-%d").date(),
                    "type_workout": type_workout,
                    "duration": w_data.get("duration"),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"  Imported {len(workouts)} workouts"))

    def import_strength_logs(self, strength_logs):
        for sl_data in strength_logs:
            try:
                exercise = Exercice.objects.get(id=sl_data["exercise_id"])
                workout = Workout.objects.get(id=sl_data["workout_id"])

                StrengthExerciseLog.objects.update_or_create(
                    id=sl_data["id"],
                    defaults={
                        "exercise": exercise,
                        "workout": workout,
                        "nb_series": sl_data.get("nb_series"),
                        "nb_repetition": sl_data.get("nb_repetition"),
                        "weight": sl_data.get("weight"),
                        "notes": sl_data.get("notes", ""),
                    },
                )
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f"  Skipping strength log {sl_data['id']}: {e}")
                )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(strength_logs)} strength logs")
        )

    def import_cardio_logs(self, cardio_logs):
        for cl_data in cardio_logs:
            try:
                exercise = Exercice.objects.get(id=cl_data["exercise_id"])
                workout = Workout.objects.get(id=cl_data["workout_id"])

                CardioExerciseLog.objects.update_or_create(
                    id=cl_data["id"],
                    defaults={
                        "exercise": exercise,
                        "workout": workout,
                        "duration_seconds": cl_data.get("duration_seconds"),
                        "distance_m": cl_data.get("distance_m"),
                        "notes": cl_data.get("notes", ""),
                    },
                )
            except (Exercice.DoesNotExist, Workout.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f"  Skipping cardio log {cl_data['id']}: {e}")
                )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(cardio_logs)} cardio logs")
        )

    def import_one_exercises(self, one_exercises):
        for oe_data in one_exercises:
            try:
                exercise = None
                if oe_data.get("exercise_id"):
                    exercise = Exercice.objects.get(id=oe_data["exercise_id"])

                workout = None
                if oe_data.get("workout_id"):
                    workout = Workout.objects.get(id=oe_data["workout_id"])

                content_type = None
                if oe_data.get("content_type_id"):
                    content_type = ContentType.objects.get(
                        id=oe_data["content_type_id"]
                    )

                OneExercice.objects.update_or_create(
                    id=oe_data["id"],
                    defaults={
                        "name": exercise,
                        "seance": workout,
                        "position": oe_data.get("position"),
                        "content_type": content_type,
                        "object_id": oe_data.get("object_id"),
                    },
                )
            except (
                Exercice.DoesNotExist,
                Workout.DoesNotExist,
                ContentType.DoesNotExist,
            ) as e:
                self.stdout.write(
                    self.style.WARNING(f"  Skipping one exercise {oe_data['id']}: {e}")
                )
        self.stdout.write(
            self.style.SUCCESS(f"  Imported {len(one_exercises)} one exercises")
        )

    def fix_sequences(self):
        """Fix PostgreSQL sequences after importing data with explicit IDs."""
        self.stdout.write("Fixing PostgreSQL sequences...")

        sql_commands = [
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_typeworkout\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_typeworkout";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_musclegroup\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_musclegroup";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_equipment\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_equipment";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_exercice\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_exercice";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_workout\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_workout";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence("
                "'\"workout_strengthexerciselog\"','id'), "
                'coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_strengthexerciselog";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence("
                "'\"workout_cardioexerciselog\"','id'), "
                'coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_cardioexerciselog";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"workout_oneexercice\"',"
                '\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "workout_oneexercice";'
            ),
        ]

        with connection.cursor() as cursor:
            for sql in sql_commands:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if result:
                        table_name = sql.split('"')[1]
                        next_id = result[0] + 1
                        self.stdout.write(
                            f"Fixed sequence for {table_name}: "
                            f"next ID will be {next_id}"
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not fix sequence: {sql} - Error: {e}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Successfully fixed all sequences!"))
