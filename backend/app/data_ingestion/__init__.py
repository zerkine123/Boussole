# ============================================
# Boussole - Data Ingestion Package
# ============================================

from app.data_ingestion.scraper import scrape_data
from app.data_ingestion.cleaner import clean_data
from app.data_ingestion.tasks import ingest_data, ingest_ons_data, ingest_custom_source

__all__ = [
    "scrape_data",
    "clean_data",
    "ingest_data",
    "ingest_ons_data",
    "ingest_custom_source",
]
