import feedparser
import re
import html
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
                    
                    image_url = self.extract_image_url(entry)
                    author = entry.get('author', '')
                    
                    clean_summary = self.clean_html_text(entry.get('summary', ''))
                    
                    article, created = Article.objects.get_or_create(
                        link=entry.link,
                        defaults={
                            'title': entry.get('title', 'No title')[:500],
                            'summary': clean_summary,
                            'published_date': published_date,
                            'source': feed,
                            'guid': entry.get('id', ''),
                            'image_url': image_url,
                            'author': author[:200] if author else '',
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

    def extract_image_url(self, entry):
        """Extract image URL from RSS entry"""
        # Check for media content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('medium') == 'image' or 'image' in media.get('type', ''):
                    return media.get('url')
        
        # Check for enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    return enclosure.get('href')
        
        # Check for media_thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url')
        
        # Look for images in summary/description
        import re
        content = entry.get('summary', '') + entry.get('description', '')
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        if img_match:
            return img_match.group(1)
        
        return None
    
    def clean_html_text(self, html_content):
        """Clean HTML content and extract readable text"""
        if not html_content:
            return ''
        
        # Decode HTML entities first
        text = html.unescape(html_content)
        
        # Remove HTML tags using regex
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Limit text length to prevent extremely long summaries
        if len(text) > 1000:
            text = text[:1000] + '...'
        
        return text