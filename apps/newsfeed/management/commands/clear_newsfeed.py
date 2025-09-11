from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.newsfeed.models import RSSFeed, Article


class Command(BaseCommand):
    help = 'Clear the entire newsfeed - delete all RSS feeds and articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without interactive prompt',
        )

    def handle(self, *args, **options):
        feed_count = RSSFeed.objects.count()
        article_count = Article.objects.count()
        total_count = feed_count + article_count
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS('Newsfeed is already empty - nothing to delete.')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'This will delete EVERYTHING from the newsfeed:')
        )
        self.stdout.write(f'  • {feed_count} RSS feeds')
        self.stdout.write(f'  • {article_count} articles')
        self.stdout.write(f'  • Total: {total_count} records')
        
        if not options['confirm']:
            confirm = input('\nAre you sure you want to CLEAR THE ENTIRE NEWSFEED? Type "CLEAR" to confirm: ')
            if confirm != 'CLEAR':
                self.stdout.write(
                    self.style.WARNING('Operation cancelled.')
                )
                return

        try:
            # Delete articles first
            if article_count > 0:
                Article.objects.all().delete()
                self.stdout.write(f'✓ Deleted {article_count} articles')
            
            # Delete RSS feeds
            if feed_count > 0:
                RSSFeed.objects.all().delete()
                self.stdout.write(f'✓ Deleted {feed_count} RSS feeds')
            
            # Clear all newsfeed cache
            cache.clear()
            self.stdout.write('✓ Cleared cache')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🧹 Successfully cleared the entire newsfeed ({total_count} records deleted)')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing newsfeed: {str(e)}')
            )