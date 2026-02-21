# ============================================
# Boussole - Celery Application Configuration
# ============================================

from celery import Celery
from app.core.config import settings

# Create Celery application
celery_app = Celery(
    "boussole",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ingestion_tasks",
        "app.tasks.insight_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Algiers",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Daily data ingestion from ONS
    "ingest-ons-data-daily": {
        "task": "app.tasks.ingestion_tasks.ingest_ons_data",
        "schedule": 86400.0,  # Every 24 hours
    },
    
    # Weekly data cleanup
    "cleanup-old-data-weekly": {
        "task": "app.tasks.ingestion_tasks.cleanup_old_data",
        "schedule": 604800.0,  # Every 7 days
    },
    
    # Hourly cache refresh
    "refresh-cache-hourly": {
        "task": "app.tasks.ingestion_tasks.refresh_cache",
        "schedule": 3600.0,  # Every hour
    },
    
    # Weekly insights generation
    "generate-weekly-insights": {
        "task": "app.tasks.insight_tasks.generate_weekly_insights",
        "schedule": 604800.0,  # Every 7 days
    },
}
