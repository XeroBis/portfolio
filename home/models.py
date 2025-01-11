from django.db import models


class Tag(models.Model):

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Projet(models.Model):
    title = models.CharField(max_length=50)

    description = models.TextField ()

    github_url = models.CharField(max_length=100)

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
    
