import json
import os

from django.core.management.base import BaseCommand
from django.db import connection

from apps.home.models import Projet, Tag, Testimonial


class Command(BaseCommand):
    help = "Import all data from data.json into Django models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data.json",
            help="Path to the JSON file to import (default: data.json)",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON file: {e}"))
            return

        self.import_tags(data.get("tags", []))
        self.import_projects(data.get("projects", []))
        self.import_testimonials(data.get("testimonials", []))

        # Fix PostgreSQL sequences after import
        self.fix_sequences()

        self.stdout.write(self.style.SUCCESS("Successfully imported all data"))

    def import_tags(self, tags_data):
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                id=tag_data["id"], defaults={"name": tag_data["name"]}
            )
            if created:
                self.stdout.write(f"Created tag: {tag.name}")
            else:
                self.stdout.write(f"Tag already exists: {tag.name}")

    def import_projects(self, projects_data):
        for project_data in projects_data:
            project, created = Projet.objects.get_or_create(
                title_en=project_data["title_en"],
                defaults={
                    "description_en": project_data["description_en"],
                    "title_fr": project_data["title_fr"],
                    "description_fr": project_data["description_fr"],
                    "github_url": project_data["github_url"],
                },
            )

            # Handle many-to-many relationships
            for tag_id in project_data.get("tags", []):
                try:
                    tag = Tag.objects.get(id=tag_id)
                    project.tags.add(tag)
                except Tag.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Tag with id {tag_id} does not exist")
                    )

            if created:
                self.stdout.write(f"Created project: {project.title_en}")
            else:
                self.stdout.write(f"Project already exists: {project.title_en}")

    def import_testimonials(self, testimonials_data):
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                id=testimonial_data["id"],
                defaults={
                    "author": testimonial_data["author"],
                    "text_en": testimonial_data["text_en"],
                    "text_fr": testimonial_data["text_fr"],
                },
            )
            if created:
                self.stdout.write(f"Created testimonial by: {testimonial.author}")
            else:
                self.stdout.write(
                    f"Testimonial already exists by: {testimonial.author}"
                )

    def fix_sequences(self):
        """Fix PostgreSQL sequences after importing data with explicit IDs."""
        self.stdout.write("Fixing PostgreSQL sequences...")

        sql_commands = [
            # Home app sequences
            (
                "SELECT setval(pg_get_serial_sequence('\"home_tag\"','id'), "
                'coalesce(max("id"), 1), max("id") IS NOT null) FROM "home_tag";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence('\"home_projet\"','id'), "
                'coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "home_projet";'
            ),
            (
                "SELECT setval(pg_get_serial_sequence("
                "'\"home_testimonial\"','id'), "
                'coalesce(max("id"), 1), max("id") IS NOT null) '
                'FROM "home_testimonial";'
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
