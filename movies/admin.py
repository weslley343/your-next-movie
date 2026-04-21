from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "year", "rank", "imdb_id")
    search_fields = ("title", "imdb_id")
    list_filter = ("year",)