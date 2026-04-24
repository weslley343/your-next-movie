from django.db import models

class SystemLog(models.Model):
    LEVEL_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="INFO")
    message = models.TextField()
    source = models.CharField(max_length=100, blank=True, null=True)

    context = models.TextField(blank=True, null=True)
    instruction = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        short_msg = self.message[:50].replace("\n", " ")
        return f"[{self.level}] {short_msg}"