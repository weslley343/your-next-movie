from rest_framework import serializers
from .models import Movie, AIInsight

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
        extra_kwargs = {
            'titulo': {'help_text': 'Ex: O Poderoso Chefão'},
            'ranking': {'help_text': 'Ex: 1'},
            'generos': {'help_text': 'Ex: Crime, Drama'},
            'data_lancamento': {'help_text': 'Ex: 1972-03-24'},
            'duracao_minutos': {'help_text': 'Ex: 175'},
        }

class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = '__all__'
