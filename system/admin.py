from django.contrib import admin
from .models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "level",
        "short_message",
        "source",
        "created_at",
    )

    list_filter = (
        "level",
        "source",
        "created_at",
    )

    search_fields = (
        "message",
        "context",
        "instruction",
        "source",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)

    # Melhor visualização no detalhe
    fieldsets = (
        ("Informações principais", {
            "fields": ("level", "source", "created_at")
        }),
        ("Mensagem", {
            "fields": ("message",)
        }),
        ("Contexto técnico", {
            "fields": ("context", "instruction"),
            "classes": ("collapse",),  # deixa colapsado no admin
        }),
    )

    # Método para não poluir a listagem
    def short_message(self, obj):
        return obj.message[:50].replace("\n", " ")

    short_message.short_description = "Message"