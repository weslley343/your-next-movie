from django.contrib import admin
from .models import Movie, AIInsight

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("ranking", "titulo", "data_lancamento", "faturamento_bruto_mundial")
    search_fields = ("titulo", "sinopse")
    list_filter = ("generos", "data_lancamento")

@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ("titulo", "created_at")
    search_fields = ("titulo", "desenvolvimento")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")