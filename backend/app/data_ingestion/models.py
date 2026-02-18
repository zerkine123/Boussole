# ============================================
# Boussole - Data Ingestion Models
# ============================================

"""
This module provides SQLAlchemy models for raw and processed data storage.
These models are used to track data ingestion pipeline status.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class RawData(Base):
    """
    RawData model for storing scraped data before processing.
    
    This table stores raw data as it's ingested from various sources.
    It serves as a staging area before data is cleaned and processed.
    """
    
    __tablename__ = "raw_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)  # e.g., 'ons', 'custom'
    source_url = Column(String(500))  # URL if scraped from web
    file_path = Column(String(500))  # Path to raw data file
    file_type = Column(String(50))  # e.g., 'csv', 'json', 'xlsx'
    record_count = Column(Integer, default=0)  # Number of records in file
    file_size = Column(Integer)  # File size in bytes
    checksum = Column(String(64))  # SHA-256 checksum for integrity
    metadata = Column(Text)  # Additional metadata as JSON
    ingestion_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)  # Error message if ingestion failed
    ingested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)  # When processing was completed
    
    # Relationships
    processed_data = relationship("ProcessedData", back_populates="raw_data", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RawData(id={self.id}, source={self.source}, status={self.ingestion_status})>"


class ProcessedData(Base):
    """
    ProcessedData model for storing cleaned and validated data.
    
    This table stores data after it has been cleaned, validated,
    and is ready to be imported into the main database tables.
    """
    
    __tablename__ = "processed_data"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_data_id = Column(Integer, ForeignKey("raw_data.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    file_path = Column(String(500))  # Path to processed data file
    record_count = Column(Integer, default=0)  # Number of records after cleaning
    records_removed = Column(Integer, default=0)  # Number of records removed during cleaning
    validation_status = Column(String(50), default="pending")  # pending, valid, invalid
    validation_issues = Column(Text)  # JSON string of validation issues
    import_status = Column(String(50), default="pending")  # pending, imported, failed
    import_errors = Column(Text)  # JSON string of import errors
    imported_at = Column(DateTime)  # When data was imported to main tables
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    raw_data = relationship("RawData", back_populates="processed_data")
    
    def __repr__(self):
        return f"<ProcessedData(id={self.id}, source={self.source}, validation_status={self.validation_status})>"


class IngestionLog(Base):
    """
    IngestionLog model for tracking data ingestion history.
    
    This table provides an audit trail of all data ingestion operations.
    """
    
    __tablename__ = "ingestion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # scrape, clean, import, validate
    task_id = Column(String(100))  # Celery task ID
    status = Column(String(50), nullable=False)  # started, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)  # Task duration in seconds
    records_processed = Column(Integer, default=0)
    records_succeeded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text)
    metadata = Column(Text)  # Additional metadata as JSON
    
    def __repr__(self):
        return f"<IngestionLog(id={self.id}, source={self.source}, task_type={self.task_type}, status={self.status})>"


class DataSource(Base):
    """
    DataSource model for managing data source configurations.
    
    This table stores configuration for various data sources
    including URLs, authentication, and scheduling information.
    """
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False)  # api, scraper, file, database
    url = Column(String(500))
    api_key = Column(String(500))  # Encrypted API key if needed
    auth_type = Column(String(50))  # none, basic, bearer, oauth
    config = Column(Text)  # Additional configuration as JSON
    is_active = Column(Boolean, default=True)
    schedule = Column(String(100))  # Cron expression for scheduled ingestion
    last_ingested_at = Column(DateTime)
    last_status = Column(String(50))  # success, failed
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, slug={self.slug}, name={self.name}, type={self.source_type})>"


class DataQualityMetric(Base):
    """
    DataQualityMetric model for tracking data quality over time.
    
    This table stores quality metrics for ingested data,
    helping to monitor data pipeline health.
    """
    
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    metric_date = Column(DateTime, nullable=False, index=True)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    completeness_score = Column(Float)  # 0.0 to 1.0
    accuracy_score = Column(Float)  # 0.0 to 1.0
    consistency_score = Column(Float)  # 0.0 to 1.0
    timeliness_score = Column(Float)  # 0.0 to 1.0
    overall_quality_score = Column(Float)  # 0.0 to 1.0
    issues = Column(Text)  # JSON string of quality issues
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DataQualityMetric(id={self.id}, source={self.source}, score={self.overall_quality_score})>"
