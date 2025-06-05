"""
SQLAlchemy models for the SF Government Document Analysis application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .database import Base


class DocumentStatus(str, enum.Enum):
    """Status of document processing."""
    PENDING = "pending"
    SCRAPED = "scraped"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    ERROR = "error"


class AnalysisType(str, enum.Enum):
    """Type of analysis performed."""
    CUSTOM_PROMPT = "custom_prompt"
    SUMMARY = "summary"
    ACTION_ITEMS = "action_items"
    TOPICS = "topics"


class Document(Base):
    """Document model for storing SF government documents."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    file_path = Column(String, nullable=True)  # S3 key
    scraped_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to analyses
    analyses = relationship("Analysis", back_populates="document")


class Analysis(Base):
    """Analysis model for storing LLM analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to document
    document = relationship("Document", back_populates="analyses") 