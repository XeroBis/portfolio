from django.contrib import admin
from .models import RSSFeed, Article


@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'url']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'published_date', 'created_at']
    list_filter = ['source', 'published_date']
    search_fields = ['title', 'summary']
    readonly_fields = ['created_at', 'published_date']
