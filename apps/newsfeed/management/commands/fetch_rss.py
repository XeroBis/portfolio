import feedparser
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime
from apps.newsfeed.models import RSSFeed, Article


class Command(BaseCommand):
    help = 'Fetch articles from RSS feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='Fetch from specific feed ID only',
        )

    def handle(self, *args, **options):
        if options['feed_id']:
            feeds = RSSFeed.objects.filter(id=options['feed_id'], is_active=True)
        else:
            feeds = RSSFeed.objects.filter(is_active=True)

        for feed in feeds:
            self.stdout.write(f'Fetching articles from {feed.name}...')
            try:
                parsed_feed = feedparser.parse(feed.url)
                
                if parsed_feed.bozo:
                    self.stdout.write(
                        self.style.WARNING(f'Warning: Feed {feed.name} has issues: {parsed_feed.bozo_exception}')
                    )

                articles_created = 0
                for entry in parsed_feed.entries:
                    published_date = self.parse_published_date(entry)
                    
                    article, created = Article.objects.get_or_create(
                        link=entry.link,
                        defaults={
                            'title': entry.get('title', 'No title')[:500],
                            'summary': entry.get('summary', ''),
                            'published_date': published_date,
                            'source': feed,
                            'guid': entry.get('id', ''),
                        }
                    )
                    
                    if created:
                        articles_created += 1

                self.stdout.write(
                    self.style.SUCCESS(f'Created {articles_created} new articles from {feed.name}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching from {feed.name}: {str(e)}')
                )

    def parse_published_date(self, entry):
        date_fields = ['published_parsed', 'updated_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return timezone.make_aware(datetime(*time_struct[:6]))
                except (ValueError, TypeError):
                    continue
        
        return timezone.now()