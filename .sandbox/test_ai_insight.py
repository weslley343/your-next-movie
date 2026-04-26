import os
import django
import sys

from dotenv import load_dotenv
load_dotenv()

# Configurar ambiente Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.services.movie_insights import generate_movie_insights
from movies.models import Movie, AIInsight
from system.models import SystemLog

def test():
    print("=== Teste de Geração de Insights IA ===")
    
    # 1. Verificar filmes
    movie_count = Movie.objects.count()
    print(f"Filmes no banco: {movie_count}")
    
    if movie_count == 0:
        print("AVISO: O banco está vazio. A IA precisa de dados de filmes para gerar insights.")
        print("Dica: Aguarde o scraper completar ou rode o scraper primeiro.")
        return

    # 2. Verificar API Key
    if not os.environ.get("GROQ_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        print("ERRO: Nenhuma API Key (GROQ ou OPENAI) encontrada no ambiente.")
        return

    print("Chamando generate_movie_insights()...")
    try:
        generate_movie_insights()
        
        # 3. Verificar resultado
        latest = AIInsight.objects.order_by('-created_at').first()
        if latest:
            print("\nSUCESSO! Insight gerado:")
            print(f"Título: {latest.titulo}")
            print(f"Introdução (primeiros 100 caracteres): {latest.introducao[:100]}...")
            print(f"Criado em: {latest.created_at}")
        else:
            print("\nFALHA: O serviço rodou mas nenhum insight foi criado no banco.")
            
        # 4. Verificar logs do sistema
        last_log = SystemLog.objects.filter(
            source__in=["groq_service", "openai_service", "insight_service"]
        ).order_by('-created_at').first()
        if last_log:
            print(f"\nÚltimo Log do Sistema: [{last_log.level}] {last_log.message}")

    except Exception as e:
        print(f"\nERRO DURANTE A EXECUÇÃO: {e}")

if __name__ == "__main__":
    test()
