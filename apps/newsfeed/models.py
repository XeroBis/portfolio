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
    image_url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    read_time_minutes = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def estimate_read_time(self):
        if self.summary:
            word_count = len(self.summary.split())
            return max(1, word_count // 200)
        return 1

    def save(self, *args, **kwargs):
        if not self.read_time_minutes:
            self.read_time_minutes = self.estimate_read_time()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['-view_count']),
        ]
