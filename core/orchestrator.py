from celery import shared_task

@shared_task
def test_log():
    from system.models import SystemLog
    SystemLog.objects.create(
        level="INFO",
        message="Celery está saudável!",
        source="celery"
    )
    return "ok"

@shared_task
def scrape_imdb_movies():
    """
    Task to scrape popular movies from IMDB.
    """
    from core.services.scrape_movies import run_imdb_scraper
    from core.services.movie_insights import generate_movie_insights
    
    run_imdb_scraper()
    generate_movie_insights()
    
    return "Scraping and Insight generation process finished"

@shared_task
def clean_health_check_logs():
    """
    Task to filter and delete logs with the message 'Celery está saudável!'.
    """
    from system.models import SystemLog
    deleted_count, _ = SystemLog.objects.filter(message="Celery está saudável!").delete()
    return f"Deleted {deleted_count} health check logs"