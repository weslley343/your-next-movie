import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from core.services.scrape_movies import run_imdb_scraper
from movies.models import Movie

def test_scraper_integration():
    print("Iniciando teste de integração do scraper...")
    
    # Limpa filmes anteriores para o teste (opcional)
    # Movie.objects.all().delete()
    
    run_imdb_scraper()
    
    # Verifica se salvou algo
    count = Movie.objects.count()
    print(f"Total de filmes no banco: {count}")
    
    if count > 0:
        first = Movie.objects.first()
        print(f"Primeiro filme: {first.titulo} ({first.duracao_minutos} min)")
    else:
        print("Nenhum filme foi salvo.")

if __name__ == "__main__":
    test_remote_selenium_check = os.getenv("SELENIUM_URL")
    if not test_remote_selenium_check:
        print("AVISO: SELENIUM_URL não está definida. O script tentará usar o driver local.")
    
    test_scraper_integration()
