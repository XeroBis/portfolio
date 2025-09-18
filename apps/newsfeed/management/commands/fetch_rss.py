import feedparser
import re
import html
import time
import requests
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
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of articles per feed (default: 20)',
        )

    def handle(self, *args, **options):
        # Configure feedparser with timeout
        feedparser.USER_AGENT = "Mozilla/5.0 (compatible; RSS Reader)"
        
        if options['feed_id']:
            feeds = RSSFeed.objects.filter(id=options['feed_id'], is_active=True)
        else:
            feeds = RSSFeed.objects.filter(is_active=True)

        limit = options['limit']
        total_feeds = feeds.count()
        processed_feeds = 0

        for feed in feeds:
            processed_feeds += 1
            self.stdout.write(f'[{processed_feeds}/{total_feeds}] Fetching articles from {feed.name}...')
            
            try:
                # Parse feed with timeout handling
                parsed_feed = self.parse_feed_with_timeout(feed.url)
                
                if not parsed_feed:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to fetch feed {feed.name} (timeout or connection error)')
                    )
                    continue
                
                if parsed_feed.bozo:
                    self.stdout.write(
                        self.style.WARNING(f'Warning: Feed {feed.name} has issues: {parsed_feed.bozo_exception}')
                    )
                    # Skip feeds with critical parsing errors
                    if "not well-formed" in str(parsed_feed.bozo_exception).lower():
                        continue

                # Limit entries to process
                entries = parsed_feed.entries[:limit]
                articles_created = 0
                
                for entry in entries:
                    try:
                        # Skip entries without required fields
                        if not hasattr(entry, 'link') or not entry.link:
                            continue
                            
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
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error processing entry from {feed.name}: {str(e)}')
                        )
                        continue

                self.stdout.write(
                    self.style.SUCCESS(f'Created {articles_created} new articles from {feed.name} (processed {len(entries)} entries)')
                )
                
                # Keep only the 10 most recent articles for this feed
                self.cleanup_old_articles(feed)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching from {feed.name}: {str(e)}')
                )
            
            # Add small delay between feeds to avoid overwhelming servers
            if processed_feeds < total_feeds:
                time.sleep(0.5)

    def parse_feed_with_timeout(self, url, timeout=10):
        """Parse RSS feed with timeout and better error handling"""
        try:
            # Use requests with timeout first to fetch the content
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader)',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Parse with feedparser
            parsed_feed = feedparser.parse(response.content)
            
            # Check if parsing was successful
            if hasattr(parsed_feed, 'feed') and hasattr(parsed_feed, 'entries'):
                return parsed_feed
            else:
                return None
                
        except requests.exceptions.Timeout:
            self.stdout.write(self.style.ERROR(f'Timeout fetching {url}'))
            return None
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Request error for {url}: {str(e)}'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error parsing {url}: {str(e)}'))
            return None

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
    
    def cleanup_old_articles(self, feed):
        """Keep only the 10 most recent articles for the given feed"""
        try:
            # Get all articles for this feed, ordered by published_date (most recent first)
            all_articles = Article.objects.filter(source=feed).order_by('-published_date')
            
            # If we have more than 10 articles, delete the older ones
            if all_articles.count() > 10:
                # Get the articles to keep (first 10)
                articles_to_keep = list(all_articles[:10])
                keep_ids = [article.id for article in articles_to_keep]
                
                # Delete articles that are not in the keep list
                deleted_count = Article.objects.filter(source=feed).exclude(id__in=keep_ids).delete()[0]
                
                if deleted_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'Cleaned up {deleted_count} old articles from {feed.name}, keeping 10 most recent')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Error cleaning up old articles for {feed.name}: {str(e)}')
            )