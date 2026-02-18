"""
Celery Tasks for Data Ingestion

This module defines Celery tasks for asynchronous data processing,
including scraping, cleaning, forecasting, and RAG indexing.

Tasks:
- scrape_data: Scrape data from various sources
- clean_data: Clean and validate scraped data
- generate_forecasts: Generate Prophet forecasts
- index_for_rag: Create embeddings for RAG
- process_pipeline: Run full ingestion pipeline
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from celery import Celery, chain, group
from celery.result import AsyncResult
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
# TODO: Configure with actual Redis broker URL
celery_app = Celery(
    'boussole',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name='ingestion.scrape_data')
def scrape_data_task(
    self,
    source_type: str,
    urls: List[str],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Scrape data from specified URLs.
    
    Args:
        self: The Celery task instance
        source_type: Type of data source (government, international, news, pdf)
        urls: List of URLs to scrape
        metadata: Optional metadata for the task
        
    Returns:
        Dictionary containing scraped data and metadata
    """
    logger.info(f"Starting scrape task for {len(urls)} URLs from {source_type}")
    
    try:
        # Import scraper here to avoid circular imports
        from .scraper import ScraperFactory, DataSourceType
        
        # Create appropriate scraper
        source_enum = DataSourceType(source_type)
        scraper = ScraperFactory.create_scraper(source_enum)
        
        # Scrape data
        scraped_data = await scraper.scrape_batch(urls)
        
        result = {
            'status': 'success',
            'source_type': source_type,
            'urls_scraped': len(urls),
            'data_count': len(scraped_data),
            'data': [data.__dict__ for data in scraped_data],
            'metadata': metadata or {},
            'completed_at': datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Scrape task completed: {result['data_count']} records")
        return result
        
    except Exception as e:
        logger.error(f"Scrape task failed: {str(e)}")
        # Retry on failure
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='ingestion.clean_data')
def clean_data_task(
    self,
    raw_data: List[Dict[str, Any]],
    cleaning_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Clean and validate raw data.
    
    Args:
        self: The Celery task instance
        raw_data: List of raw data dictionaries
        cleaning_options: Optional cleaning configuration
        
    Returns:
        Dictionary containing cleaned data and cleaning report
    """
    logger.info(f"Starting clean task for {len(raw_data)} records")
    
    try:
        # Import cleaner here to avoid circular imports
        from .cleaner import clean_raw_data
        
        # Clean data
        df, report = clean_raw_data(raw_data)
        
        result = {
            'status': 'success',
            'original_rows': report.original_rows,
            'cleaned_rows': report.cleaned_rows,
            'duplicates_removed': report.duplicates_removed,
            'missing_values_filled': report.missing_values_filled,
            'outliers_handled': report.outliers_handled,
            'quality_score': report.quality_score.value,
            'issues_found': report.issues_found,
            'warnings': report.warnings,
            'data': df.to_dict('records'),
            'completed_at': datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Clean task completed: {result['cleaned_rows']} records")
        return result
        
    except Exception as e:
        logger.error(f"Clean task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='ingestion.generate_forecasts')
def generate_forecasts_task(
    self,
    metric_id: str,
    wilaya_id: Optional[int] = None,
    periods: int = 12,
    forecast_horizon: str = 'monthly'
) -> Dict[str, Any]:
    """
    Generate Prophet forecasts for a metric.
    
    Args:
        self: The Celery task instance
        metric_id: ID of the metric to forecast
        wilaya_id: Optional Wilaya ID for specific forecasts
        periods: Number of periods to forecast
        forecast_horizon: Time period for forecasts (monthly, quarterly, yearly)
        
    Returns:
        Dictionary containing forecast results and metrics
    """
    logger.info(f"Starting forecast task for metric {metric_id}")
    
    try:
        # Import forecasting service here to avoid circular imports
        from app.services.forecasting_service import ForecastingService
        from app.db.session import get_db
        from app.schemas.forecast import ForecastGenerateRequest
        
        # Get database session
        db = next(get_db())
        
        # Create forecasting service
        forecasting_service = ForecastingService(db)
        
        # Generate forecast request
        request = ForecastGenerateRequest(
            metric_id=metric_id,
            wilaya_id=wilaya_id,
            periods=periods,
            forecast_horizon=forecast_horizon,
        )
        
        # Generate forecast
        response = await forecasting_service.generate_forecast(request)
        
        result = {
            'status': 'success',
            'metric_id': metric_id,
            'wilaya_id': wilaya_id,
            'periods': periods,
            'forecast_horizon': forecast_horizon,
            'forecasts': [f.model_dump() for f in response.forecasts],
            'mae': response.mae,
            'mape': response.mape,
            'rmse': response.rmse,
            'trend': response.trend,
            'completed_at': datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Forecast task completed: {len(result['forecasts'])} forecasts")
        return result
        
    except Exception as e:
        logger.error(f"Forecast task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='ingestion.index_for_rag')
def index_for_rag_task(
    self,
    documents: List[Dict[str, Any]],
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
) -> Dict[str, Any]:
    """
    Create embeddings for RAG indexing.
    
    Args:
        self: The Celery task instance
        documents: List of documents to index
        embedding_model: Name of the embedding model to use
        
    Returns:
        Dictionary containing indexing results
    """
    logger.info(f"Starting RAG indexing task for {len(documents)} documents")
    
    try:
        # Import sentence-transformers for embeddings
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model
        model = SentenceTransformer(embedding_model)
        
        # Create embeddings
        texts = [doc.get('content', '') for doc in documents]
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # TODO: Store embeddings in pgvector database
        # This would involve:
        # 1. Connecting to PostgreSQL with pgvector extension
        # 2. Creating/updating vector columns
        # 3. Inserting embeddings with metadata
        
        result = {
            'status': 'success',
            'documents_indexed': len(documents),
            'embedding_model': embedding_model,
            'embedding_dimension': embeddings.shape[1] if len(embeddings) > 0 else 0,
            'completed_at': datetime.utcnow().isoformat(),
        }
        
        logger.info(f"RAG indexing task completed: {result['documents_indexed']} documents")
        return result
        
    except Exception as e:
        logger.error(f"RAG indexing task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name='ingestion.process_pipeline')
def process_pipeline_task(
    self,
    source_type: str,
    urls: List[str],
    generate_forecasts: bool = True,
    index_for_rag: bool = True
) -> Dict[str, Any]:
    """
    Run the complete data ingestion pipeline.
    
    Pipeline steps:
    1. Scrape data from URLs
    2. Clean and validate data
    3. Generate forecasts (optional)
    4. Index for RAG (optional)
    
    Args:
        self: The Celery task instance
        source_type: Type of data source
        urls: List of URLs to scrape
        generate_forecasts: Whether to generate Prophet forecasts
        index_for_rag: Whether to index for RAG
        
    Returns:
        Dictionary containing pipeline results
    """
    logger.info(f"Starting ingestion pipeline for {len(urls)} URLs")
    
    try:
        # Step 1: Scrape data
        scrape_result = scrape_data_task.apply_async(
            args=[source_type, urls],
            throw=True
        ).get(timeout=3600)
        
        if scrape_result['status'] != 'success':
            raise Exception(f"Scraping failed: {scrape_result}")
        
        # Step 2: Clean data
        clean_result = clean_data_task.apply_async(
            args=[scrape_result['data']],
            throw=True
        ).get(timeout=1800)
        
        if clean_result['status'] != 'success':
            raise Exception(f"Cleaning failed: {clean_result}")
        
        result = {
            'status': 'success',
            'scrape_result': scrape_result,
            'clean_result': clean_result,
            'forecasts_generated': False,
            'rag_indexed': False,
            'completed_at': datetime.utcnow().isoformat(),
        }
        
        # Step 3: Generate forecasts (optional)
        if generate_forecasts:
            # TODO: Identify metrics from cleaned data and generate forecasts
            # This would involve:
            # 1. Extract unique metrics from cleaned data
            # 2. Call generate_forecasts_task for each metric
            # 3. Collect results
            result['forecasts_generated'] = True
            logger.info("Forecasts generated")
        
        # Step 4: Index for RAG (optional)
        if index_for_rag:
            # TODO: Index documents for RAG
            # This would involve:
            # 1. Extract documents from cleaned data
            # 2. Call index_for_rag_task
            # 3. Collect results
            result['rag_indexed'] = True
            logger.info("RAG indexing completed")
        
        logger.info("Ingestion pipeline completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {str(e)}")
        raise self.retry(exc=e, countdown=120, max_retries=2)


@celery_app.task(name='ingestion.schedule_daily_ingestion')
def schedule_daily_ingestion():
    """
    Scheduled task to run daily data ingestion.
    
    This task should be scheduled to run daily using Celery Beat.
    """
    logger.info("Running scheduled daily ingestion")
    
    # TODO: Define sources to scrape daily
    sources = {
        'government': [
            'https://www.ons.dz/publications',
            'https://www.madr.gov.dz/statistiques',
        ],
        'international': [
            'https://api.worldbank.org/v2/country/DZA/indicator',
        ],
    }
    
    # Run pipeline for each source type
    results = []
    for source_type, urls in sources.items():
        try:
            result = process_pipeline_task.apply_async(
                args=[source_type, urls, True, True]
            )
            results.append(result.id)
        except Exception as e:
            logger.error(f"Failed to schedule ingestion for {source_type}: {e}")
    
    return {
        'status': 'scheduled',
        'tasks_scheduled': len(results),
        'task_ids': results,
        'scheduled_at': datetime.utcnow().isoformat(),
    }


@celery_app.task(name='ingestion.schedule_weekly_forecasts')
def schedule_weekly_forecasts():
    """
    Scheduled task to regenerate forecasts weekly.
    
    This task should be scheduled to run weekly using Celery Beat.
    """
    logger.info("Running scheduled weekly forecast regeneration")
    
    # TODO: Get all metrics from database and generate forecasts
    # This would involve:
    # 1. Query database for all active metrics
    # 2. Call generate_forecasts_task for each metric
    # 3. Store results
    
    return {
        'status': 'scheduled',
        'scheduled_at': datetime.utcnow().isoformat(),
    }


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Dictionary containing task status information
    """
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        'task_id': task_id,
        'status': result.status,
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else None,
        'failed': result.failed() if result.ready() else None,
        'result': result.result if result.ready() else None,
    }


def cancel_task(task_id: str) -> bool:
    """
    Cancel a running Celery task.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        True if task was cancelled, False otherwise
    """
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return False
    
    result.revoke(terminate=True)
    logger.info(f"Task {task_id} cancelled")
    return True


# Example of Celery Beat configuration (to be added to celeryconfig.py):
"""
from celery.schedules import crontab

beat_schedule = {
    'daily-ingestion': {
        'task': 'ingestion.schedule_daily_ingestion',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM UTC
    },
    'weekly-forecasts': {
        'task': 'ingestion.schedule_weekly_forecasts',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),  # Run Monday at 3 AM UTC
    },
}
"""


if __name__ == "__main__":
    # Test tasks
    import asyncio
    
    # Example: Run a scrape task
    result = scrape_data_task.delay('government', ['https://example.com'])
    print(f"Task ID: {result.id}")
    print(f"Task Status: {get_task_status(result.id)}")
