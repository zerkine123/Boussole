# ============================================
# Boussole - RAG (Retrieval-Augmented Generation) Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/query")
async def query_rag(
    query_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Query the RAG system with a natural language question.
    
    - **query**: The question or query text
    - **language**: Query language (en, fr, ar)
    - **sector_slug**: Optional sector to focus the search
    - **top_k**: Number of relevant documents to retrieve (default: 5)
    
    Returns an AI-generated answer with source references.
    """
    service = RAGService(db)
    
    query = query_data.get("query")
    language = query_data.get("language", "en")
    sector_slug = query_data.get("sector_slug")
    top_k = query_data.get("top_k", 5)
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required"
        )
    
    result = await service.query(
        query=query,
        language=language,
        sector_slug=sector_slug,
        top_k=top_k
    )
    
    return result


@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    sector_slug: Optional[str] = None,
    language: str = "en",
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for indexing in the RAG system.
    
    - **file**: Document file (PDF, DOCX, TXT)
    - **title**: Document title (optional, defaults to filename)
    - **sector_slug**: Associated sector (optional)
    - **language**: Document language (en, fr, ar)
    """
    service = RAGService(db)
    
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: PDF, DOCX, TXT"
        )
    
    # Process and index the document
    result = await service.upload_document(
        file=file,
        title=title,
        sector_slug=sector_slug,
        language=language
    )
    
    return result


@router.get("/documents")
async def list_documents(
    sector_slug: Optional[str] = None,
    language: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List indexed documents with optional filtering.
    """
    service = RAGService(db)
    return await service.list_documents(
        sector_slug=sector_slug,
        language=language,
        skip=skip,
        limit=limit
    )


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific document by ID.
    """
    service = RAGService(db)
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document from the RAG system.
    """
    service = RAGService(db)
    success = await service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )


@router.post("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Re-index a document (update embeddings).
    """
    service = RAGService(db)
    result = await service.reindex_document(document_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"message": "Document re-indexed successfully"}
