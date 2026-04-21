from celery import shared_task
from system.models import SystemLog

@shared_task
def test_log():
    SystemLog.objects.create(
        level="INFO",
        message="Celery executou a task!",
        source="celery"
    )
    return "ok"