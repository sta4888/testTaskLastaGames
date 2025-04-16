from celery import Celery


# Здесь тоже нужно поправить
app = Celery(
    'tasks',
    broker='redis://lesta-games-redis:6379/0',
    backend='redis://lesta-games-redis:6379/0'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

app.autodiscover_tasks(['tasks'])