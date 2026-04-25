from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("ranking", "titulo", "data_lancamento", "faturamento_bruto_mundial")
    search_fields = ("titulo", "sinopse")
    list_filter = ("generos", "data_lancamento")