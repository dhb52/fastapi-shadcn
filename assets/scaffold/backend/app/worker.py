from celery import Celery

from app.core.config import settings

celery_app = Celery("app", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
)


@celery_app.task  # type: ignore[untyped-decorator]
def ping() -> str:
    return "pong"
