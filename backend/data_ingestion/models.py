"""
Data Ingestion Models

This module defines SQLAlchemy models for raw and processed data
used in the data ingestion pipeline.

Models:
- RawData: Stores scraped data before processing
- ProcessedData: Stores cleaned and validated data
- IngestionJob: Tracks data ingestion jobs and their status
- DataSource: Metadata about data sources
"""

import logging
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, JSON, Float, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from app.db.base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Enumeration of ingestion job statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class DataSourceType(str, Enum):
    """Enumeration of data source types."""
    GOVERNMENT = "government"
    INTERNATIONAL = "international"
    NEWS = "news"
    ACADEMIC = "academic"
    PDF = "pdf"
    MANUAL = "manual"


class RawData(Base):
    """
    Model for storing raw scraped data.
    
    This table stores data as-is from scraping before any processing.
    It serves as an audit trail and allows for re-processing if needed.
    """
    __tablename__ = "raw_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ingestion_job_id = Column(Integer, ForeignKey('ingestion_jobs.id'), index=True)
    
    # Source information
    source_type = Column(String(50), nullable=False, index=True)
    source_url = Column(Text, nullable=True)
    source_name = Column(String(255), nullable=True, index=True)
    
    # Raw content
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Store any additional raw data
    
    # Metadata
    published_date = Column(DateTime, nullable=True, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    language = Column(String(10), default='en', nullable=True)
    
    # Processing flags
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    ingestion_job = relationship("IngestionJob", back_populates="raw_data")
    processed_data = relationship("ProcessedData", back_populates="raw_data", uselist=False)
    
    def __repr__(self):
        return f"<RawData(id={self.id}, source_type={self.source_type}, title={self.title})>"


class ProcessedData(Base):
    """
    Model for storing cleaned and processed data.
    
    This table stores data after cleaning and validation.
    It's the primary data source for analytics and forecasting.
    """
    __tablename__ = "processed_data"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'), nullable=False, index=True)
    
    # Wilaya information
    wilaya_id = Column(Integer, ForeignKey('wilayas.id'), index=True)
    wilaya_code = Column(String(10), nullable=False, index=True)
    wilaya_name = Column(String(100), nullable=False)
    
    # Sector information
    sector_id = Column(Integer, ForeignKey('sectors.id'), index=True)
    sector_name = Column(String(100), nullable=False, index=True)
    
    # Metric information
    metric_id = Column(Integer, ForeignKey('indicators.id'), index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    
    # Time information
    period = Column(String(50), nullable=False, index=True)  # e.g., '2024-Q1', '2024-01'
    year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=True, index=True)
    month = Column(Integer, nullable=True, index=True)
    
    # Data quality flags
    is_verified = Column(Boolean, default=False, nullable=False)
    is_anomaly = Column(Boolean, default=False, nullable=False, index=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadata
    processing_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_processed_wilaya_year', 'wilaya_code', 'year'),
        Index('idx_processed_sector_year', 'sector_name', 'year'),
        Index('idx_processed_metric_period', 'metric_name', 'period'),
    )
    
    # Relationships
    raw_data = relationship("RawData", back_populates="processed_data")
    
    def __repr__(self):
        return f"<ProcessedData(id={self.id}, wilaya={self.wilaya_code}, sector={self.sector_name}, value={self.metric_value})>"


class IngestionJob(Base):
    """
    Model for tracking data ingestion jobs.
    
    This table tracks all ingestion operations including:
    - Scraping jobs
    - Cleaning jobs
    - Forecast generation jobs
    - RAG indexing jobs
    """
    __tablename__ = "ingestion_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job information
    job_type = Column(String(50), nullable=False, index=True)  # scrape, clean, forecast, index
    job_name = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, index=True, default=JobStatus.PENDING.value)
    
    # Source information
    source_type = Column(String(50), nullable=False, index=True)
    source_urls = Column(JSON, nullable=True)  # List of URLs
    
    # Processing configuration
    config = Column(JSON, nullable=True)  # Job configuration options
    
    # Results and metrics
    records_processed = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    records_skipped = Column(Integer, default=0, nullable=False)
    
    # Quality metrics
    quality_score = Column(String(20), nullable=True)  # excellent, good, fair, poor
    duplicates_removed = Column(Integer, default=0, nullable=False)
    missing_values_filled = Column(Integer, default=0, nullable=False)
    outliers_handled = Column(Integer, default=0, nullable=False)
    
    # Forecasting metrics
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    mape = Column(Float, nullable=True)  # Mean Absolute Percentage Error
    rmse = Column(Float, nullable=True)  # Root Mean Square Error
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Celery task tracking
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Relationships
    raw_data = relationship("RawData", back_populates="ingestion_job")
    
    def __repr__(self):
        return f"<IngestionJob(id={self.id}, type={self.job_type}, status={self.status})>"
    
    def mark_as_running(self):
        """Mark job as running."""
        self.status = JobStatus.RUNNING.value
        self.started_at = datetime.utcnow()
    
    def mark_as_completed(self, records_processed: int):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.records_processed = records_processed
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
    
    def mark_as_failed(self, error_message: str):
        """Mark job as failed."""
        self.status = JobStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
    
    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.status = JobStatus.RETRYING.value


class DataSource(Base):
    """
    Model for storing data source metadata.
    
    This table tracks all data sources including:
    - Government websites
    - International organization APIs
    - News outlets
    - Academic publications
    """
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source identification
    source_type = Column(String(50), nullable=False, index=True)
    source_name = Column(String(255), nullable=False, unique=True, index=True)
    source_url = Column(String(500), nullable=True)
    source_code = Column(String(50), nullable=True, unique=True)  # e.g., 'ons', 'world_bank'
    
    # Source configuration
    api_endpoint = Column(String(500), nullable=True)
    api_key_required = Column(Boolean, default=False, nullable=False)
    authentication_type = Column(String(50), nullable=True)  # api_key, oauth, none
    
    # Source metadata
    description = Column(Text, nullable=True)
    language = Column(String(10), default='en', nullable=True)
    data_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, yearly
    
    # Status and reliability
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_reliable = Column(Boolean, default=True, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    last_scrape_status = Column(String(20), nullable=True)
    scrape_success_count = Column(Integer, default=0, nullable=False)
    scrape_failure_count = Column(Integer, default=0, nullable=False)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.source_name}, type={self.source_type})>"
    
    def get_success_rate(self) -> float:
        """Calculate the success rate of scraping this source."""
        total = self.scrape_success_count + self.scrape_failure_count
        if total == 0:
            return 0.0
        return (self.scrape_success_count / total) * 100


class DataQualityMetrics(Base):
    """
    Model for storing data quality metrics over time.
    
    This table tracks data quality metrics for monitoring
    and improvement of the ingestion pipeline.
    """
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period = Column(String(50), nullable=False, index=True)  # e.g., '2024-01'
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True, index=True)
    
    # Quality metrics
    total_records = Column(Integer, nullable=False)
    complete_records = Column(Integer, nullable=False)  # Records with no missing values
    duplicate_records = Column(Integer, nullable=False)
    outlier_records = Column(Integer, nullable=False)
    
    # Quality scores
    completeness_score = Column(Float, nullable=False)  # % of records with no missing values
    uniqueness_score = Column(Float, nullable=False)  # % of unique records
    validity_score = Column(Float, nullable=False)  # % of records passing validation
    overall_quality_score = Column(Float, nullable=False)
    
    # Trends
    quality_trend = Column(String(20), nullable=True)  # improving, stable, declining
    
    # Metadata
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<DataQualityMetrics(id={self.id}, period={self.period}, score={self.overall_quality_score})>"


def create_ingestion_tables(engine):
    """
    Create all ingestion-related tables.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Ingestion tables created successfully")


def drop_ingestion_tables(engine):
    """
    Drop all ingestion-related tables.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(bind=engine)
    logger.info("Ingestion tables dropped")


# Example queries for common operations
"""
# Get all raw data for a source
raw_data_by_source = session.query(RawData).filter(
    RawData.source_type == 'government',
    RawData.is_processed == False
).all()

# Get processed data for a Wilaya and year
processed_data = session.query(ProcessedData).filter(
    ProcessedData.wilaya_code == '01',
    ProcessedData.year == 2024
).order_by(ProcessedData.period).all()

# Get recent ingestion jobs
recent_jobs = session.query(IngestionJob).filter(
    IngestionJob.started_at >= datetime.utcnow() - timedelta(days=7)
).order_by(IngestionJob.started_at.desc()).all()

# Get data quality trend
quality_trend = session.query(DataQualityMetrics).filter(
    DataQualityMetrics.year == 2024
).order_by(DataQualityMetrics.month).all()
"""
