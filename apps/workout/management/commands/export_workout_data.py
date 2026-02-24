import json
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.workout.models import (
    CardioExerciseLog,
    CardioSeriesLog,
    Equipment,
    Exercice,
    MuscleGroup,
    OneExercice,
    StrengthExerciseLog,
    StrengthSeriesLog,
    TypeWorkout,
    Workout,
)


class Command(BaseCommand):
    help = "Export all workout data to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="workout_data.json",
            help="Output file path (default: workout_data.json)",
        )

    def handle(self, *args, **kwargs):
        today_date = datetime.today().strftime("%Y-%m-%d")

        output_path: str = kwargs.get("output", "workout_data.json")

        data = {
            "export_date": today_date,
            "type_workouts": self.export_type_workouts(),
            "muscle_groups": self.export_muscle_groups(),
            "equipment": self.export_equipment(),
            "exercises": self.export_exercises(),
            "workouts": self.export_workouts(),
            "strength_series_logs": self.export_strength_series_logs(),
            "cardio_series_logs": self.export_cardio_series_logs(),
            # Legacy data - will be empty for new workouts but kept for backward compatibility
            "strength_exercise_logs": self.export_strength_logs(),
            "cardio_exercise_logs": self.export_cardio_logs(),
            "one_exercises": self.export_one_exercises(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"All workout data exported successfully to {output_path}"
            )
        )

    def export_type_workouts(self):
        return [
            {
                "id": tw.id,
                "name_workout": tw.name_workout,
            }
            for tw in TypeWorkout.objects.all()
        ]

    def export_muscle_groups(self):
        return [
            {
                "id": mg.id,
                "name": mg.name,
                "description": mg.description,
            }
            for mg in MuscleGroup.objects.all()
        ]

    def export_equipment(self):
        return [
            {
                "id": eq.id,
                "name": eq.name,
                "description": eq.description,
            }
            for eq in Equipment.objects.all()
        ]

    def export_exercises(self):
        return [
            {
                "id": ex.id,
                "name": ex.name,
                "exercise_type": ex.exercise_type,
                "difficulty": ex.difficulty,
                "muscle_groups": [mg.id for mg in ex.muscle_groups.all()],
                "equipment": [eq.id for eq in ex.equipment.all()],
            }
            for ex in Exercice.objects.all()
        ]

    def export_workouts(self):
        return [
            {
                "id": w.id,
                "date": w.date.strftime("%Y-%m-%d"),
                "type_workout_id": w.type_workout.id if w.type_workout else None,
                "type_workout_name": (
                    w.type_workout.name_workout if w.type_workout else None
                ),
                "duration": w.duration,
            }
            for w in Workout.objects.all()
        ]

    def export_strength_series_logs(self):
        return [
            {
                "id": ssl.id,
                "exercise_id": ssl.exercise.id,
                "exercise_name": ssl.exercise.name,
                "workout_id": ssl.workout.id,
                "series_number": ssl.series_number,
                "reps": ssl.reps,
                "weight": ssl.weight,
            }
            for ssl in StrengthSeriesLog.objects.all()
        ]

    def export_cardio_series_logs(self):
        return [
            {
                "id": csl.id,
                "exercise_id": csl.exercise.id,
                "exercise_name": csl.exercise.name,
                "workout_id": csl.workout.id,
                "series_number": csl.series_number,
                "duration_seconds": csl.duration_seconds,
                "distance_m": csl.distance_m,
            }
            for csl in CardioSeriesLog.objects.all()
        ]

    def export_strength_logs(self):
        return [
            {
                "id": sl.id,
                "exercise_id": sl.exercise.id,
                "exercise_name": sl.exercise.name,
                "workout_id": sl.workout.id,
                "nb_series": sl.nb_series,
                "nb_repetition": sl.nb_repetition,
                "weight": sl.weight,
                "notes": sl.notes,
            }
            for sl in StrengthExerciseLog.objects.all()
        ]

    def export_cardio_logs(self):
        return [
            {
                "id": cl.id,
                "exercise_id": cl.exercise.id,
                "exercise_name": cl.exercise.name,
                "workout_id": cl.workout.id,
                "duration_seconds": cl.duration_seconds,
                "distance_m": cl.distance_m,
                "notes": cl.notes,
            }
            for cl in CardioExerciseLog.objects.all()
        ]

    def export_one_exercises(self):
        return [
            {
                "id": oe.id,
                "exercise_id": oe.name.id if oe.name else None,
                "exercise_name": oe.name.name if oe.name else None,
                "workout_id": oe.seance.id if oe.seance else None,
                "workout_date": (
                    oe.seance.date.strftime("%Y-%m-%d") if oe.seance else None
                ),
                "position": oe.position,
                "content_type_id": oe.content_type.id if oe.content_type else None,
                "object_id": oe.object_id,
                "exercise_log_data": oe.get_display_data() if oe.exercise_log else None,
            }
            for oe in OneExercice.objects.all()
        ]
