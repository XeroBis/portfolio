from django.contrib import admin
from .models import RSSFeed, Article


@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'url']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'author', 'is_featured', 'view_count', 'read_time_minutes', 'published_date']
    list_filter = ['source', 'published_date', 'is_featured', 'source__category']
    search_fields = ['title', 'summary', 'author']
    readonly_fields = ['created_at', 'published_date', 'view_count', 'read_time_minutes']
    list_editable = ['is_featured']
    actions = ['mark_as_featured', 'mark_as_not_featured']
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'link', 'summary')
        }),
        ('Metadata', {
            'fields': ('author', 'image_url', 'tags', 'source', 'guid')
        }),
        ('Display Settings', {
            'fields': ('is_featured',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'read_time_minutes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_date', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} articles marked as featured.')
    mark_as_featured.short_description = "Mark selected articles as featured"
    
    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} articles unmarked as featured.')
    mark_as_not_featured.short_description = "Unmark selected articles as featured"
