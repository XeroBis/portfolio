from django.db import models
from django.utils import timezone


class RSSFeed(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Article(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    summary = models.TextField(blank=True)
    published_date = models.DateTimeField()
    source = models.ForeignKey(RSSFeed, on_delete=models.CASCADE, related_name='articles')
    guid = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
        ]
