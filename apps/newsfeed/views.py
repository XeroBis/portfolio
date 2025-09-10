from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, F
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Article, RSSFeed
import io
import sys
import json


def home(request):
    cache_key = f"newsfeed_articles_{request.GET.urlencode()}"
    cached_context = cache.get(cache_key)
    
    if cached_context:
        return render(request, 'newsfeed/newsfeed_home.html', cached_context)
    
    articles = Article.objects.select_related('source').all()
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(summary__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Category filtering
    category = request.GET.get('category')
    if category:
        articles = articles.filter(source__category=category)
    
    # Sorting options
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'popular':
        articles = articles.order_by('-view_count', '-published_date')
    elif sort_by == 'featured':
        articles = articles.order_by('-is_featured', '-published_date')
    else:
        articles = articles.order_by('-published_date')
    
    # Pagination
    page_size = int(request.GET.get('per_page', 20))
    paginator = Paginator(articles, min(page_size, 50))  # Max 50 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and featured articles
    categories = RSSFeed.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    categories = list(set(categories))
    
    featured_articles = Article.objects.filter(is_featured=True).order_by('-published_date')[:3]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
        'current_sort': sort_by,
        'featured_articles': featured_articles,
        'total_articles': paginator.count,
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, context, 300)
    
    return render(request, 'newsfeed/newsfeed_home.html', context)


@staff_member_required
def fetch_feeds(request):
    if request.method == 'POST':
        try:
            # Capture command output
            out = io.StringIO()
            call_command('fetch_rss', stdout=out)
            output = out.getvalue()
            
            # Parse output to count new articles
            lines = output.strip().split('\n')
            total_new = 0
            for line in lines:
                if 'Created' in line and 'new articles' in line:
                    try:
                        count = int(line.split('Created ')[1].split(' new articles')[0])
                        total_new += count
                    except (ValueError, IndexError):
                        pass
            
            if total_new > 0:
                messages.success(request, f'Successfully fetched {total_new} new articles!')
            else:
                messages.info(request, 'No new articles found.')
                
        except Exception as e:
            messages.error(request, f'Error fetching feeds: {str(e)}')
    
    return redirect('newsfeed:home')


def article_detail(request, pk):
    """Track article views and redirect to external link"""
    try:
        article = Article.objects.get(pk=pk)
        # Increment view count
        Article.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        
        # Clear cache when view count changes
        # LocMemCache doesn't support delete_pattern, so we use cache versioning
        from django.core.cache import caches
        default_cache = caches['default']
        
        # Get all cache keys and delete those matching our pattern
        if hasattr(default_cache, '_cache'):
            # For LocMemCache, manually find and delete matching keys
            keys_to_delete = []
            for key in default_cache._cache.keys():
                if 'newsfeed_articles_' in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                default_cache.delete(key)
        
        return redirect(article.link)
    except Article.DoesNotExist:
        messages.error(request, "Article not found")
        return redirect('newsfeed:home')


@staff_member_required
def export_rss_feeds(request):
    """Export all RSS feeds as JSON"""
    feeds = RSSFeed.objects.all().values(
        'name', 'url', 'category', 'is_active'
    )
    
    feeds_data = {
        'rss_feeds': list(feeds),
        'export_date': timezone.now().isoformat(),
        'total_feeds': len(feeds)
    }
    
    response = HttpResponse(
        json.dumps(feeds_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="rss_feeds_export.json"'
    return response


@staff_member_required  
@require_http_methods(["POST"])
def import_rss_feeds(request):
    """Import RSS feeds from uploaded JSON file"""
    if 'feed_file' not in request.FILES:
        messages.error(request, 'No file was uploaded.')
        return redirect('newsfeed:home')
    
    feed_file = request.FILES['feed_file']
    
    if not feed_file.name.endswith('.json'):
        messages.error(request, 'Please upload a JSON file.')
        return redirect('newsfeed:home')
    
    try:
        file_content = feed_file.read().decode('utf-8')
        data = json.loads(file_content)
        
        if 'rss_feeds' not in data:
            messages.error(request, 'Invalid file format. Expected "rss_feeds" key.')
            return redirect('newsfeed:home')
        
        feeds_to_import = data['rss_feeds']
        imported_count = 0
        skipped_count = 0
        
        for feed_data in feeds_to_import:
            # Validate required fields
            if not all(key in feed_data for key in ['name', 'url']):
                continue
                
            # Check if feed already exists
            if RSSFeed.objects.filter(url=feed_data['url']).exists():
                skipped_count += 1
                continue
            
            # Create new feed
            RSSFeed.objects.create(
                name=feed_data['name'],
                url=feed_data['url'],
                category=feed_data.get('category', ''),
                is_active=feed_data.get('is_active', True)
            )
            imported_count += 1
        
        if imported_count > 0:
            messages.success(request, f'Successfully imported {imported_count} RSS feeds.')
        if skipped_count > 0:
            messages.info(request, f'Skipped {skipped_count} duplicate feeds.')
            
        if imported_count == 0 and skipped_count == 0:
            messages.warning(request, 'No valid feeds found in the file.')
            
    except json.JSONDecodeError:
        messages.error(request, 'Invalid JSON file format.')
    except Exception as e:
        messages.error(request, f'Error importing feeds: {str(e)}')
    
    return redirect('newsfeed:home')
