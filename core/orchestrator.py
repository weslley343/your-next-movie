from celery import shared_task

@shared_task
def test_log():
    from system.models import SystemLog
    SystemLog.objects.create(
        level="INFO",
        message="Celery executou a task!",
        source="celery"
    )
    return "ok"

@shared_task
def scrape_imdb_movies():
    """
    Task to scrape popular movies from IMDB.
    Currently only logs the execution.
    """
    from system.models import SystemLog
    SystemLog.objects.create(
        level="INFO",
        message="Iniciando scraping de filmes do IMDB...",
        source="celery.scraper"
    )
    return "Scraping task started"