# ============================================
# Boussole - Data Ingestion API Endpoint
# ============================================

"""
API endpoints for the Data Ingestion Pipeline.

POST /api/v1/ingestion/csv    — Upload a CSV file for ingestion
POST /api/v1/ingestion/api    — Pull data from an external API
GET  /api/v1/ingestion/status — Get ingestion pipeline status
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.data_ingestion.connectors import CSVUploadConnector, APIConnector
from app.services.ingestion_pipeline_service import IngestionPipelineService

router = APIRouter()


@router.post("/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    source_label: str = Form("csv_upload"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV file and ingest its data into the database.
    
    The CSV should have columns like:
    indicator, value, year, sector, wilaya_code, unit, source
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        content = await file.read()
        csv_text = content.decode("utf-8")

        connector = CSVUploadConnector(csv_text, source_label=source_label)
        records = await connector.run()

        if not records:
            return {
                "status": "warning",
                "message": "No valid records found in the CSV",
                "stats": {"created": 0, "updated": 0, "skipped": 0, "errors": 0},
            }

        pipeline = IngestionPipelineService(db)
        stats = await pipeline.ingest(records)

        return {
            "status": "success",
            "message": f"Ingested {stats['created']} new records, updated {stats['updated']}",
            "stats": stats,
            "source": source_label,
            "filename": file.filename,
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="File encoding error. Please use UTF-8."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.post("/api")
async def ingest_from_api(
    url: str,
    json_path: Optional[str] = None,
    source_label: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Pull data from an external REST API and ingest it.
    
    Args:
        url: The API endpoint URL
        json_path: Dot-separated path to drill into the JSON response (e.g. "data.results")
        source_label: Label for the data source
    """
    try:
        path_list = json_path.split(".") if json_path else []
        connector = APIConnector(
            url=url,
            json_path=path_list,
            source_label=source_label or url,
        )
        records = await connector.run()

        if not records:
            return {
                "status": "warning",
                "message": "No valid records found from the API",
                "stats": {"created": 0, "updated": 0, "skipped": 0, "errors": 0},
            }

        pipeline = IngestionPipelineService(db)
        stats = await pipeline.ingest(records)

        return {
            "status": "success",
            "message": f"Ingested {stats['created']} new records, updated {stats['updated']}",
            "stats": stats,
            "source": source_label or url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API ingestion failed: {e}")


@router.get("/status")
async def ingestion_status():
    """Get the current status of the ingestion pipeline."""
    return {
        "status": "operational",
        "connectors": ["csv_upload", "api"],
        "message": "Data ingestion pipeline is ready",
    }
