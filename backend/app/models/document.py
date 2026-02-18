# ============================================
# Boussole - Document Model (for RAG)
# ============================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Document(Base):
    """
    Document model for storing documents used in RAG (Retrieval-Augmented Generation).
    """
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_en = Column(String(500))
    title_fr = Column(String(500))
    title_ar = Column(String(500))
    content = Column(Text)  # Full text content
    summary = Column(Text)  # AI-generated summary
    source = Column(String(200))  # Source (e.g., "ONS Report", "Government Gazette")
    source_url = Column(String(500))
    document_type = Column(String(50))  # e.g., "report", "article", "press_release"
    language = Column(String(10))  # en, fr, ar
    file_path = Column(String(500))  # Path to stored file
    file_size = Column(Integer)  # File size in bytes
    file_type = Column(String(50))  # e.g., "pdf", "docx", "txt"
    sector_id = Column(Integer, ForeignKey("sectors.id", ondelete="SET NULL"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_published = Column(Boolean, default=False)
    is_indexed = Column(Boolean, default=False)  # Whether indexed for vector search
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sector = relationship("Sector")
    owner = relationship("User")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, type={self.document_type})>"


class DocumentEmbedding(Base):
    """
    DocumentEmbedding model for storing vector embeddings of document chunks.
    Uses pgvector for similarity search.
    """
    
    __tablename__ = "document_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Index of the chunk within the document
    chunk_text = Column(Text, nullable=False)  # The actual text chunk
    embedding = Column(LargeBinary, nullable=False)  # Vector embedding (pgvector)
    meta_data = Column(Text)  # Additional metadata as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    
    def __repr__(self):
        return f"<DocumentEmbedding(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
