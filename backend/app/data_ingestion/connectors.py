# ============================================
# Boussole - Data Ingestion Connectors
# ============================================

"""
Modular connector interface for the Data Ingestion Pipeline.
Each connector knows how to extract data from a specific source type
and normalise it into a common format for loading into the database.
"""

import csv
import io
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Common data format: every connector yields rows of NormalizedRecord
# ------------------------------------------------------------------

class NormalizedRecord:
    """
    Flat, source-agnostic representation of one data point.
    All connectors must transform their raw data into this shape
    before handing it off to the pipeline.
    """

    def __init__(
        self,
        *,
        indicator_name: str,
        value: float,
        period: str = "annual",
        year: Optional[int] = None,
        quarter: Optional[str] = None,
        month: Optional[int] = None,
        unit: Optional[str] = None,
        sector: Optional[str] = None,
        wilaya_code: Optional[str] = None,
        source: Optional[str] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.indicator_name = indicator_name
        self.value = value
        self.period = period
        self.year = year or datetime.utcnow().year
        self.quarter = quarter
        self.month = month
        self.unit = unit
        self.sector = sector
        self.wilaya_code = wilaya_code
        self.source = source
        self.source_url = source_url
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_name": self.indicator_name,
            "value": self.value,
            "period": self.period,
            "year": self.year,
            "quarter": self.quarter,
            "month": self.month,
            "unit": self.unit,
            "sector": self.sector,
            "wilaya_code": self.wilaya_code,
            "source": self.source,
            "source_url": self.source_url,
            "metadata": self.metadata,
        }


# ------------------------------------------------------------------
# Base Connector
# ------------------------------------------------------------------

class BaseConnector(ABC):
    """
    Abstract base class for all data connectors.
    Subclasses must implement `extract()` and `transform()`.
    """

    name: str = "base"

    @abstractmethod
    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Pull raw data from the source.
        Returns a list of raw dictionaries.
        """
        ...

    @abstractmethod
    async def transform(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[NormalizedRecord]:
        """
        Convert raw dicts into NormalizedRecord instances.
        """
        ...

    async def run(self, **kwargs) -> List[NormalizedRecord]:
        """Full extract→transform pipeline."""
        logger.info(f"[{self.name}] Starting extraction…")
        raw = await self.extract(**kwargs)
        logger.info(f"[{self.name}] Extracted {len(raw)} raw rows")
        records = await self.transform(raw)
        logger.info(f"[{self.name}] Transformed into {len(records)} normalized records")
        return records


# ------------------------------------------------------------------
# CSV Upload Connector
# ------------------------------------------------------------------

class CSVUploadConnector(BaseConnector):
    """
    Connector for user-uploaded CSV files.

    Expected CSV columns (case-insensitive, flexible naming):
      - indicator / name / metric        → indicator_name
      - value / amount / number           → value
      - year                              → year
      - quarter / q                       → quarter
      - month                             → month
      - unit                              → unit
      - sector / industry                 → sector
      - wilaya / wilaya_code / region     → wilaya_code
      - source                            → source
    """

    name = "csv_upload"

    # Column aliases → canonical field name
    COLUMN_MAP = {
        "indicator": "indicator_name",
        "name": "indicator_name",
        "metric": "indicator_name",
        "indicator_name": "indicator_name",
        "value": "value",
        "amount": "value",
        "number": "value",
        "year": "year",
        "quarter": "quarter",
        "q": "quarter",
        "month": "month",
        "unit": "unit",
        "sector": "sector",
        "industry": "sector",
        "wilaya": "wilaya_code",
        "wilaya_code": "wilaya_code",
        "region": "wilaya_code",
        "source": "source",
    }

    def __init__(self, csv_content: str, source_label: str = "csv_upload"):
        self.csv_content = csv_content
        self.source_label = source_label

    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Parse CSV string into list of dicts."""
        reader = csv.DictReader(io.StringIO(self.csv_content))
        rows: List[Dict[str, Any]] = []
        for raw_row in reader:
            # Normalise column names
            row: Dict[str, Any] = {}
            for col, val in raw_row.items():
                key = self.COLUMN_MAP.get(col.strip().lower(), col.strip().lower())
                row[key] = val.strip() if val else None
            rows.append(row)
        return rows

    async def transform(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[NormalizedRecord]:
        records: List[NormalizedRecord] = []
        for row in raw_data:
            try:
                value = float(row.get("value", 0))
            except (ValueError, TypeError):
                logger.warning(f"Skipping row with non-numeric value: {row}")
                continue

            records.append(
                NormalizedRecord(
                    indicator_name=row.get("indicator_name", "unknown"),
                    value=value,
                    year=int(row["year"]) if row.get("year") else None,
                    quarter=row.get("quarter"),
                    month=int(row["month"]) if row.get("month") else None,
                    unit=row.get("unit"),
                    sector=row.get("sector"),
                    wilaya_code=row.get("wilaya_code"),
                    source=self.source_label,
                )
            )
        return records


# ------------------------------------------------------------------
# REST API Connector
# ------------------------------------------------------------------

class APIConnector(BaseConnector):
    """
    Generic connector for pulling JSON data from a REST API.
    The caller provides a `json_path` list of keys to drill into
    the response to find the list of records.
    """

    name = "api"

    def __init__(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json_path: Optional[List[str]] = None,
        source_label: Optional[str] = None,
    ):
        self.url = url
        self.headers = headers or {}
        self.json_path = json_path or []
        self.source_label = source_label or url

    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        # Drill into nested JSON
        for key in self.json_path:
            data = data[key]

        if isinstance(data, list):
            return data
        return [data]

    async def transform(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[NormalizedRecord]:
        """
        Default transform expects each item to have at least
        'indicator_name' and 'value' keys.
        Override in a subclass for custom mapping.
        """
        records: List[NormalizedRecord] = []
        for item in raw_data:
            try:
                records.append(
                    NormalizedRecord(
                        indicator_name=str(
                            item.get("indicator_name")
                            or item.get("name")
                            or item.get("indicator")
                            or "unknown"
                        ),
                        value=float(item.get("value", 0)),
                        year=int(item["year"]) if item.get("year") else None,
                        unit=item.get("unit"),
                        sector=item.get("sector"),
                        wilaya_code=str(item.get("wilaya_code", "")) or None,
                        source=self.source_label,
                        source_url=self.url,
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping API row: {e}")
        return records
