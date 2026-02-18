"""
Data Ingestion Module

This module handles all data ingestion operations including:
- Web scraping from various sources
- Data cleaning and validation
- Prophet forecasting
- RAG indexing with embeddings
- Celery task management
"""

from .scraper import (
    BaseScraper,
    GovernmentScraper,
    InternationalScraper,
    NewsScraper,
    PDFScraper,
    ScraperFactory,
    DataSourceType,
    ScrapedData,
)

from .cleaner import (
    DataCleaner,
    CleaningReport,
    DataQuality,
    clean_raw_data,
    standardize_wilaya_name,
    standardize_sector_name,
)

from .tasks import (
    celery_app,
    scrape_data_task,
    clean_data_task,
    generate_forecasts_task,
    index_for_rag_task,
    process_pipeline_task,
    schedule_daily_ingestion,
    schedule_weekly_forecasts,
    get_task_status,
    cancel_task,
)

from .models import (
    RawData,
    ProcessedData,
    IngestionJob,
    DataSource,
    DataQualityMetrics,
    JobStatus,
    DataSourceType as IngestionDataSourceType,
    create_ingestion_tables,
    drop_ingestion_tables,
)

__all__ = [
    # Scrapers
    'BaseScraper',
    'GovernmentScraper',
    'InternationalScraper',
    'NewsScraper',
    'PDFScraper',
    'ScraperFactory',
    'DataSourceType',
    'ScrapedData',
    # Cleaners
    'DataCleaner',
    'CleaningReport',
    'DataQuality',
    'clean_raw_data',
    'standardize_wilaya_name',
    'standardize_sector_name',
    # Tasks
    'celery_app',
    'scrape_data_task',
    'clean_data_task',
    'generate_forecasts_task',
    'index_for_rag_task',
    'process_pipeline_task',
    'schedule_daily_ingestion',
    'schedule_weekly_forecasts',
    'get_task_status',
    'cancel_task',
    # Models
    'RawData',
    'ProcessedData',
    'IngestionJob',
    'DataSource',
    'DataQualityMetrics',
    'JobStatus',
    'IngestionDataSourceType',
    'create_ingestion_tables',
    'drop_ingestion_tables',
]

__version__ = '1.0.0'
