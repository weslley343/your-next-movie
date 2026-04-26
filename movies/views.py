from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import Movie, AIInsight
from .serializers import MovieSerializer, AIInsightSerializer

@extend_schema(
    description="Endpoints para gerenciar filmes populares.",
    examples=[
        OpenApiExample(
            'Exemplo de Filme',
            value={
                'ranking': 1,
                'titulo': 'The Shawshank Redemption',
                'sinopse': 'Two imprisoned men bond over a number of years...',
                'generos': 'Drama',
                'data_lancamento': '1994-09-22',
                'duracao_minutos': 142
            },
            request_only=True,
        )
    ]
)
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('ranking')
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['generos', 'data_lancamento']
    search_fields = ['titulo', 'sinopse']
    ordering_fields = ['ranking', 'data_lancamento', 'duracao_minutos']

class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints para visualizar os insights gerados pela IA.
    (Apenas leitura, pois os insights são gerados automaticamente pelo sistema)
    """
    queryset = AIInsight.objects.all().order_by('-created_at')
    serializer_class = AIInsightSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['created_at']
    search_fields = ['titulo', 'desenvolvimento']
    ordering_fields = ['created_at', 'titulo']
