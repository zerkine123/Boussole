# ============================================
# Boussole - Embeddings Module
# ============================================

"""
Text embeddings generation using sentence-transformers.

This module provides functions for:
- Loading embedding models
- Generating text embeddings
- Managing embedding cache
"""

import logging
from typing import List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Wrapper class for sentence-transformers embedding model.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """
        Load the embedding model.
        """
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for encoding
            show_progress_bar: Whether to show progress bar
        
        Returns:
            NumPy array of embeddings
        """
        if self._model is None:
            self._load_model()
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress_bar,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}", exc_info=True)
            raise
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to encode
        
        Returns:
            NumPy array of embedding
        """
        return self.encode(text)[0]
    
    def get_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            Embedding dimension
        """
        if self._model is None:
            self._load_model()
        return self._model.get_sentence_embedding_dimension()


# Global embedding model instance
embedding_model = EmbeddingModel()


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text string to encode
    
    Returns:
        List of embedding values
    
    Example:
        >>> embedding = generate_embedding("Hello world")
        >>> print(len(embedding))
        384
    """
    try:
        embedding = embedding_model.encode_single(text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return []


def generate_embeddings(
    texts: List[str],
    batch_size: int = 32
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of text strings to encode
        batch_size: Batch size for encoding
    
    Returns:
        List of embedding lists
    
    Example:
        >>> texts = ["Hello", "World"]
        >>> embeddings = generate_embeddings(texts)
        >>> print(len(embeddings))
        2
    """
    try:
        embeddings = embedding_model.encode(texts, batch_size=batch_size)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return []


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[str]:
    """
    Split text into chunks for embedding generation.
    
    Args:
        text: Text to split into chunks
        chunk_size: Maximum size of each chunk (in characters)
        chunk_overlap: Overlap between chunks (in characters)
    
    Returns:
        List of text chunks
    
    Example:
        >>> text = "This is a long text that needs to be chunked."
        >>> chunks = chunk_text(text, chunk_size=20)
        >>> print(len(chunks))
        3
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks


def calculate_similarity(
    embedding1: List[float],
    embedding2: List[float]
) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score (0 to 1)
    
    Example:
        >>> sim = calculate_similarity(embedding1, embedding2)
        >>> print(f"Similarity: {sim:.2f}")
        Similarity: 0.85
    """
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    except Exception as e:
        logger.error(f"Failed to calculate similarity: {e}")
        return 0.0


def prepare_document_for_indexing(
    document_id: int,
    content: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[dict]:
    """
    Prepare a document for indexing by chunking and generating embeddings.
    
    Args:
        document_id: Document ID
        content: Document content
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of dictionaries with chunk text and embeddings
    
    Example:
        >>> chunks = prepare_document_for_indexing(1, "Long document content...")
        >>> print(len(chunks))
        10
    """
    # Split content into chunks
    text_chunks = chunk_text(content, chunk_size, chunk_overlap)
    
    # Generate embeddings for all chunks
    embeddings = generate_embeddings(text_chunks)
    
    # Prepare chunk data
    chunk_data = []
    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        chunk_data.append({
            "document_id": document_id,
            "chunk_index": i,
            "chunk_text": chunk,
            "embedding": embedding,
        })
    
    return chunk_data
