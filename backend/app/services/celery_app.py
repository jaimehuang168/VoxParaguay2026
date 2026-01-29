"""
VoxParaguay 2026 - Celery Application
Async task processing for AI analysis and report generation
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "voxparaguay",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.services.tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task

    # Beat schedule for automated tasks
    beat_schedule={
        # Generate daily report at midnight (00:00 PYT)
        "generate-daily-reports": {
            "task": "app.services.tasks.generate_daily_reports",
            "schedule": {
                "hour": 0,
                "minute": 0,
            },
        },
        # Sync analytics cache every 5 minutes
        "update-analytics-cache": {
            "task": "app.services.tasks.update_analytics_cache",
            "schedule": 300.0,  # 5 minutes
        },
    },
)
