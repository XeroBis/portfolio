from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.newsfeed.models import RSSFeed, Article


class Command(BaseCommand):
    help = 'Delete all RSS feeds and their associated articles from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without interactive prompt',
        )
        parser.add_argument(
            '--feeds-only',
            action='store_true',
            help='Delete only feeds, keep articles (articles will become orphaned)',
        )

    def handle(self, *args, **options):
        feed_count = RSSFeed.objects.count()
        article_count = Article.objects.count()
        
        if feed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No RSS feeds found to delete.')
            )
            return

        if options['feeds_only']:
            self.stdout.write(f'Found {feed_count} RSS feeds to delete.')
            self.stdout.write(
                self.style.WARNING(f'Warning: {article_count} articles will become orphaned.')
            )
        else:
            self.stdout.write(f'Found {feed_count} RSS feeds and {article_count} articles to delete.')
        
        if not options['confirm']:
            if options['feeds_only']:
                confirm = input('Are you sure you want to delete ALL RSS feeds (articles will remain)? Type "yes" to confirm: ')
            else:
                confirm = input('Are you sure you want to delete ALL RSS feeds AND articles? Type "yes" to confirm: ')
            
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.WARNING('Operation cancelled.')
                )
                return

        try:
            if not options['feeds_only']:
                # Delete articles first (cascade should handle this, but being explicit)
                Article.objects.all().delete()
                self.stdout.write(f'Deleted {article_count} articles.')
            
            # Delete RSS feeds
            RSSFeed.objects.all().delete()
            
            # Clear the newsfeed cache
            cache.clear()
            
            if options['feeds_only']:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {feed_count} RSS feeds.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {feed_count} RSS feeds and {article_count} articles.')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting data: {str(e)}')
            )