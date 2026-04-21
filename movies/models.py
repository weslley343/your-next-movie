from django.db import models

class Movie(models.Model):
    imdb_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.year})"