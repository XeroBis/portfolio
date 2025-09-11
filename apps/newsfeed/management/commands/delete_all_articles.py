from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.newsfeed.models import Article


class Command(BaseCommand):
    help = 'Delete all articles from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without interactive prompt',
        )

    def handle(self, *args, **options):
        article_count = Article.objects.count()
        
        if article_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No articles found to delete.')
            )
            return

        self.stdout.write(f'Found {article_count} articles to delete.')
        
        if not options['confirm']:
            confirm = input('Are you sure you want to delete ALL articles? Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.WARNING('Operation cancelled.')
                )
                return

        try:
            Article.objects.all().delete()
            
            # Clear the newsfeed cache
            cache.clear()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {article_count} articles.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting articles: {str(e)}')
            )