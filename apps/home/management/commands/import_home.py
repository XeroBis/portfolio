import json
from django.core.management.base import BaseCommand
from apps.home.models import Tag, Projet, Testimonial

class Command(BaseCommand):
    help = 'Import Tag, Projet, and Testimonial models from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument("file_name", nargs=1, type=str)

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs["file_name"][0], "r", encoding="utf-8") as f:
                data = json.load(f)

            tag_map = {}
            for tag_data in data.get("tags", []):
                tag, _ = Tag.objects.get_or_create(id=tag_data["id"], defaults={"name": tag_data["name"]})
                tag_map[tag_data["id"]] = tag

            project_map = {}
            for project_data in data.get("projects", []):
                project, _ = Projet.objects.update_or_create(
                    id=project_data["id"],
                    defaults={
                        "title_en": project_data["title_en"],
                        "description_en": project_data["description_en"],
                        "title_fr": project_data["title_fr"],
                        "description_fr": project_data["description_fr"],
                        "github_url": project_data["github_url"]
                    }
                )
                project_map[project_data["id"]] = project

            for project_data in data.get("projects", []):
                project = project_map.get(project_data["id"])
                if project:
                    project.tags.set([tag_map[tag_id] for tag_id in project_data.get("tags", []) if tag_id in tag_map])

            for testimonial_data in data.get("testimonials", []):
                Testimonial.objects.update_or_create(
                    id=testimonial_data["id"],
                    defaults={
                        "author": testimonial_data["author"],
                        "text_en": testimonial_data["text_en"],
                        "text_fr": testimonial_data["text_fr"]
                    }
                )

            self.stdout.write(self.style.SUCCESS('Data successfully imported from exported_data.json'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('the file name you provied is not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {e}'))