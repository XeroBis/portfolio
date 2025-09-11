import feedparser
import re
import html
import time
import requests
import threading
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime
from apps.newsfeed.models import RSSFeed, Article, FeedFetchTask


class Command(BaseCommand):
    help = 'Fetch articles from RSS feeds asynchronously'

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
        # Create a new task
        task = FeedFetchTask.objects.create(status='pending')
        
        # Start the background thread
        thread = threading.Thread(
            target=self.run_async_fetch,
            args=(task.id, options)
        )
        thread.daemon = True
        thread.start()
        
        self.stdout.write(
            self.style.SUCCESS(f'Background fetch task {task.id} started. Check progress with --task-id {task.id}')
        )

    def run_async_fetch(self, task_id, options):
        """Run the fetch process in the background"""
        task = FeedFetchTask.objects.get(id=task_id)
        
        try:
            task.status = 'running'
            task.started_at = timezone.now()
            task.save()
            
            # Configure feedparser
            feedparser.USER_AGENT = "Mozilla/5.0 (compatible; RSS Reader)"
            
            if options['feed_id']:
                feeds = RSSFeed.objects.filter(id=options['feed_id'], is_active=True)
            else:
                feeds = RSSFeed.objects.filter(is_active=True)

            task.total_feeds = feeds.count()
            task.save()

            limit = options['limit']
            processed_feeds = 0
            total_articles_created = 0

            for feed in feeds:
                processed_feeds += 1
                task.processed_feeds = processed_feeds
                task.progress_text = f'Processing {feed.name}... ({processed_feeds}/{task.total_feeds})'
                task.save()
                
                try:
                    # Parse feed with timeout handling
                    parsed_feed = self.parse_feed_with_timeout(feed.url, task)
                    
                    if not parsed_feed:
                        self.log_error(task, f'Failed to fetch feed {feed.name} (timeout or connection error)')
                        continue
                    
                    if parsed_feed.bozo:
                        self.log_error(task, f'Warning: Feed {feed.name} has issues: {parsed_feed.bozo_exception}')
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
                                total_articles_created += 1
                                
                        except Exception as e:
                            self.log_error(task, f'Error processing entry from {feed.name}: {str(e)}')
                            continue

                    task.progress_text = f'Completed {feed.name} - {articles_created} new articles'
                    task.articles_created = total_articles_created
                    task.save()
                    
                except Exception as e:
                    self.log_error(task, f'Error fetching from {feed.name}: {str(e)}')
                
                # Add small delay between feeds
                if processed_feeds < task.total_feeds:
                    time.sleep(0.5)
            
            # Mark as completed
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.progress_text = f'Completed! Processed {task.total_feeds} feeds, created {total_articles_created} new articles'
            task.save()
            
        except Exception as e:
            task.status = 'failed'
            task.completed_at = timezone.now()
            self.log_error(task, f'Fatal error: {str(e)}')

    def log_error(self, task, error_message):
        """Add error message to task"""
        if task.errors:
            task.errors += f"\n{error_message}"
        else:
            task.errors = error_message
        task.save()

    def parse_feed_with_timeout(self, url, task, timeout=10):
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
            self.log_error(task, f'Timeout fetching {url}')
            return None
        except requests.exceptions.RequestException as e:
            self.log_error(task, f'Request error for {url}: {str(e)}')
            return None
        except Exception as e:
            self.log_error(task, f'Unexpected error parsing {url}: {str(e)}')
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