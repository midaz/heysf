"""
Analysis API router.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Analysis, Document
from ..schemas import AnalysisResponse
from ..services.analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{document_id}", response_model=List[AnalysisResponse])
def get_analysis_by_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get all analyses for a specific document.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        List of analyses for the document
    """
    # Check if document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analyses = db.query(Analysis).filter(Analysis.document_id == document_id).all()
    return analyses


@router.get("/", response_model=List[AnalysisResponse])
def list_all_analyses(
    skip: int = 0,
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all analyses across all documents.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of all analyses
    """
    analyses = db.query(Analysis).offset(skip).limit(limit).all()
    return analyses


@router.post("/analyze-all")
def analyze_all_pending():
    """
    Trigger analysis for all pending documents.
    
    Returns:
        Number of documents analyzed
    """
    try:
        from ..database import SessionLocal
        db = SessionLocal()
        
        analyzer = DocumentAnalyzer()
        analyzed_count = analyzer.analyze_pending_documents(db)
        
        db.close()
        
        return {
            "message": f"Analysis completed for {analyzed_count} documents",
            "analyzed_count": analyzed_count
        }
        
    except Exception as e:
        logger.error(f"Error during batch analysis: {e}")
        raise HTTPException(status_code=500, detail="Error during batch analysis") 