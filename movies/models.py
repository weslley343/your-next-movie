from django.db import models

class Movie(models.Model):
    ranking = models.IntegerField(null=True, blank=True)
    titulo = models.CharField(max_length=255)
    sinopse = models.TextField(null=True, blank=True)
    faturamento_bruto_mundial = models.BigIntegerField(null=True, blank=True)
    generos = models.CharField(max_length=255, null=True, blank=True)
    data_lancamento = models.DateField(null=True, blank=True)
    duracao_minutos = models.IntegerField(null=True, blank=True)
    proporcao = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

class AIInsight(models.Model):
    titulo = models.CharField(max_length=255)
    introducao = models.TextField()
    desenvolvimento = models.TextField()
    conclusao = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo