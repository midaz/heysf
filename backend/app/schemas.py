"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .models import DocumentStatus, AnalysisType


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    url: str


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    pass


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    file_path: Optional[str] = None
    status: DocumentStatus
    scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisBase(BaseModel):
    """Base analysis schema."""
    analysis_type: AnalysisType
    content: str


class AnalysisCreate(AnalysisBase):
    """Schema for creating an analysis."""
    document_id: int


class AnalysisResponse(AnalysisBase):
    """Schema for analysis response."""
    id: int
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentWithAnalyses(DocumentResponse):
    """Document with its analyses."""
    analyses: List[AnalysisResponse] = []


class ScrapingResponse(BaseModel):
    """Response for scraping operations."""
    message: str
    documents_found: int
    documents_scraped: int


class AnalysisRequest(BaseModel):
    """Request to analyze a document."""
    custom_prompt: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    database_connected: bool
    total_documents: int
    analyzed_documents: int 