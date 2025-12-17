"""
Celery application for background tasks
"""
from celery import Celery
from core.config import settings

# Initialize Celery
celery_app = Celery(
    "drug_repurposing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['services.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.AGENT_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.AGENT_TIMEOUT_SECONDS - 30,
)
