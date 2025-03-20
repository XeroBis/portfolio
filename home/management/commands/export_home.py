import json
from django.core.management.base import BaseCommand
from home.models import Tag, Projet, Testimonial
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Export Tag, Projet, and Testimonial models to a JSON file'

    def handle(self, *args, **kwargs):

        today_date = datetime.today().strftime('%Y-%m-%d')
        is_prod = "PROD" if os.getenv('IS_PROD', False) == 'True' else "LOCAL"
        json_file_path = f'data/{is_prod}/home_{is_prod}_{today_date}.json'
        
        data = {
            "tags": list(Tag.objects.values("id", "name")),
            "projects": list(Projet.objects.values(
                "id", "title_en", "description_en", "title_fr", "description_fr", "github_url"
            )),
            "testimonials": list(Testimonial.objects.values("id", "author", "text_en", "text_fr")),
        }
        
        for project in data["projects"]:
            project["tags"] = list(Projet.objects.get(id=project["id"]).tags.values_list("id", flat=True))
        
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS('Data successfully exported to exported_data.json'))
