import json
from django.core.management.base import BaseCommand
from apps.home.models import Tag, Projet, Testimonial


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
            "testimonials": list(Testimonial.objects.values())
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