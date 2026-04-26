from django.http import JsonResponse

def home(request):
    """
    Exibe a proposta do projeto e link para o Swagger em formato JSON.
    """
    return JsonResponse({
        "projeto": "Your Next Movie",
        "proposta": "Your Next Movie é uma plataforma que combina análise inteligente de tendências e descoberta de filmes, ajudando você a dar o próximo passo certeiro no universo do cinema",
        "documentacao": {
            "swagger": request.build_absolute_uri("/api/docs/swagger/"),
            "redoc": request.build_absolute_uri("/api/docs/redoc/")
        }
    })
