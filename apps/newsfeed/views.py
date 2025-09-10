from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Article, RSSFeed
import io
import sys


def home(request):
    articles = Article.objects.select_related('source').all()
    
    category = request.GET.get('category')
    if category:
        articles = articles.filter(source__category=category)
    
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = RSSFeed.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    categories = list(set(categories))
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
    }
    
    return render(request, 'newsfeed/home.html', context)


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
