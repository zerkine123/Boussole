# ============================================
# Boussole - Vector Retriever Module
# ============================================

"""
Vector similarity search using pgvector.

This module provides functions for:
- Storing embeddings in PostgreSQL with pgvector
- Performing similarity search
- Retrieving relevant document chunks
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import generate_embedding, calculate_similarity
from app.core.config import settings

logger = logging.getLogger(__name__)


async def store_embedding(
    db: AsyncSession,
    document_id: int,
    chunk_index: int,
    chunk_text: str,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store an embedding in the database.
    
    Args:
        db: Database session
        document_id: Document ID
        chunk_index: Index of the chunk within the document
        chunk_text: Text content of the chunk
        embedding: Embedding vector
        metadata: Optional metadata as dictionary
    
    Returns:
        ID of the created embedding record
    
    Example:
        >>> embedding_id = await store_embedding(db, 1, 0, "Hello world", [0.1, 0.2, ...])
        >>> print(f"Stored embedding with ID: {embedding_id}")
    """
    try:
        # Convert embedding to binary format for pgvector
        import struct
        embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Insert embedding into database
        query = text("""
            INSERT INTO document_embeddings 
            (document_id, chunk_index, chunk_text, embedding, metadata)
            VALUES (:document_id, :chunk_index, :chunk_text, :embedding, :metadata)
            RETURNING id
        """)
        
        result = await db.execute(
            query,
            {
                "document_id": document_id,
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "embedding": embedding_bytes,
                "metadata": metadata_json,
            }
        )
        
        embedding_id = result.scalar_one()
        await db.commit()
        
        logger.info(f"Stored embedding for document {document_id}, chunk {chunk_index}")
        return embedding_id
    
    except Exception as e:
        logger.error(f"Failed to store embedding: {e}", exc_info=True)
        await db.rollback()
        raise


async def similarity_search(
    db: AsyncSession,
    query_text: str,
    top_k: int = 5,
    sector_id: Optional[int] = None,
    language: Optional[str] = None,
    threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Perform similarity search for a query.
    
    Args:
        db: Database session
        query_text: Query text to search for
        top_k: Number of results to return
        sector_id: Optional sector filter
        language: Optional language filter
        threshold: Minimum similarity threshold (0 to 1)
    
    Returns:
        List of matching document chunks with similarity scores
    
    Example:
        >>> results = await similarity_search(db, "What is the GDP?", top_k=3)
        >>> for result in results:
        ...     print(f"Score: {result['similarity']:.2f} - {result['chunk_text'][:50]}...")
    """
    try:
        # Generate embedding for query
        query_embedding = generate_embedding(query_text)
        
        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []
        
        # Convert embedding to binary format for pgvector
        import struct
        embedding_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
        
        # Build query with optional filters
        where_clause = "WHERE 1=1"
        params = {"embedding": embedding_bytes, "limit": top_k}
        
        if sector_id:
            where_clause += " AND d.sector_id = :sector_id"
            params["sector_id"] = sector_id
        
        if language:
            where_clause += " AND d.language = :language"
            params["language"] = language
        
        if threshold is not None:
            where_clause += " AND similarity >= :threshold"
            params["threshold"] = threshold
        
        # Perform similarity search using pgvector
        query = text(f"""
            SELECT 
                de.id,
                de.document_id,
                de.chunk_index,
                de.chunk_text,
                d.title,
                d.source,
                d.language,
                de.metadata,
                1 - (de.embedding <=> :embedding) as similarity
            FROM document_embeddings de
            JOIN documents d ON de.document_id = d.id
            {where_clause}
            AND d.is_published = true
            ORDER BY similarity DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "chunk_text": row[3],
                "title": row[4],
                "source": row[5],
                "language": row[6],
                "metadata": json.loads(row[7]) if row[7] else None,
                "similarity": float(row[8]),
            })
        
        logger.info(f"Found {len(results)} similar chunks for query: {query_text[:50]}...")
        return results
    
    except Exception as e:
        logger.error(f"Failed to perform similarity search: {e}", exc_info=True)
        return []


async def delete_document_embeddings(
    db: AsyncSession,
    document_id: int
) -> int:
    """
    Delete all embeddings for a document.
    
    Args:
        db: Database session
        document_id: Document ID
    
    Returns:
        Number of deleted embeddings
    
    Example:
        >>> count = await delete_document_embeddings(db, 1)
        >>> print(f"Deleted {count} embeddings")
    """
    try:
        query = text("""
            DELETE FROM document_embeddings
            WHERE document_id = :document_id
            RETURNING id
        """)
        
        result = await db.execute(query, {"document_id": document_id})
        deleted_ids = result.fetchall()
        await db.commit()
        
        count = len(deleted_ids)
        logger.info(f"Deleted {count} embeddings for document {document_id}")
        return count
    
    except Exception as e:
        logger.error(f"Failed to delete embeddings: {e}", exc_info=True)
        await db.rollback()
        raise


async def get_document_embeddings(
    db: AsyncSession,
    document_id: int
) -> List[Dict[str, Any]]:
    """
    Get all embeddings for a document.
    
    Args:
        db: Database session
        document_id: Document ID
    
    Returns:
        List of embedding records
    
    Example:
        >>> embeddings = await get_document_embeddings(db, 1)
        >>> print(f"Found {len(embeddings)} chunks")
    """
    try:
        query = text("""
            SELECT 
                id,
                chunk_index,
                chunk_text,
                metadata,
                created_at
            FROM document_embeddings
            WHERE document_id = :document_id
            ORDER BY chunk_index
        """)
        
        result = await db.execute(query, {"document_id": document_id})
        rows = result.fetchall()
        
        embeddings = []
        for row in rows:
            embeddings.append({
                "id": row[0],
                "chunk_index": row[1],
                "chunk_text": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "created_at": row[4],
            })
        
        return embeddings
    
    except Exception as e:
        logger.error(f"Failed to get document embeddings: {e}", exc_info=True)
        return []


async def reindex_document(
    db: AsyncSession,
    document_id: int,
    content: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> int:
    """
    Re-index a document by deleting old embeddings and creating new ones.
    
    Args:
        db: Database session
        document_id: Document ID
        content: New document content
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
    
    Returns:
        Number of new embeddings created
    
    Example:
        >>> count = await reindex_document(db, 1, "Updated content...")
        >>> print(f"Created {count} new embeddings")
    """
    try:
        # Delete old embeddings
        await delete_document_embeddings(db, document_id)
        
        # Prepare new chunks
        from app.ai.embeddings import prepare_document_for_indexing
        chunk_data = prepare_document_for_indexing(
            document_id,
            content,
            chunk_size,
            chunk_overlap
        )
        
        # Store new embeddings
        for chunk in chunk_data:
            await store_embedding(
                db,
                chunk["document_id"],
                chunk["chunk_index"],
                chunk["chunk_text"],
                chunk["embedding"]
            )
        
        logger.info(f"Re-indexed document {document_id} with {len(chunk_data)} chunks")
        return len(chunk_data)
    
    except Exception as e:
        logger.error(f"Failed to re-index document: {e}", exc_info=True)
        raise
