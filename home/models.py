from django.db import models


class Tag(models.Model):

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Projet(models.Model):

    title_en = models.CharField(max_length=50)
    description_en = models.TextField()

    title_fr = models.CharField(max_length=50)
    description_fr = models.TextField()

    github_url = models.CharField(max_length=100)

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title_en
    
class Testimonial(models.Model):

    author = models.CharField(max_length=50)

    text_en = models.TextField()
    text_fr = models.TextField()
    
    def __str__(self):
        return self.author