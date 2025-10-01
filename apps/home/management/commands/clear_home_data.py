from django.core.management.base import BaseCommand
from apps.home.models import Projet, Tag, Testimonial


class Command(BaseCommand):
    help = 'Clear all home data from the database'

    def handle(self, *args, **options):
        self.stdout.write('Clearing home data...')

        # Delete all home data
        projet_count = Projet.objects.count()
        tag_count = Tag.objects.count()
        testimonial_count = Testimonial.objects.count()

        Projet.objects.all().delete()
        Tag.objects.all().delete()
        Testimonial.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleared home data:\n'
                f'  - {projet_count} projects deleted\n'
                f'  - {tag_count} tags deleted\n'
                f'  - {testimonial_count} testimonials deleted'
            )
        )
