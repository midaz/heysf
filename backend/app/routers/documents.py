"""
Documents API router.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, DocumentStatus
from ..schemas import DocumentResponse, DocumentWithAnalyses, ScrapingResponse, AnalysisRequest
from ..services.scraper import SFBOSScraper
from ..services.analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0, 
    limit: int = 100,
    status: DocumentStatus = None,
    db: Session = Depends(get_db)
):
    """
    List all documents with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by document status
        db: Database session
        
    Returns:
        List of documents
    """
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentWithAnalyses)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get a specific document with its analyses.
    
    Args:
        document_id: ID of the document
        db: Database session
        
    Returns:
        Document with analyses
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.post("/scrape", response_model=ScrapingResponse)
def scrape_documents(db: Session = Depends(get_db)):
    """
    Manually trigger document scraping.
    
    Args:
        db: Database session
        
    Returns:
        Scraping results
    """
    try:
        scraper = SFBOSScraper()
        
        # Check for new documents
        new_documents = scraper.check_for_new_documents(db)
        documents_found = len(new_documents)
        
        # Scrape content for new documents
        documents_scraped = 0
        for document in new_documents:
            if scraper.scrape_document(document, db):
                documents_scraped += 1
        
        return ScrapingResponse(
            message=f"Scraping completed. Found {documents_found} new documents, scraped {documents_scraped}",
            documents_found=documents_found,
            documents_scraped=documents_scraped
        )
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail="Error during scraping")


@router.post("/{document_id}/analyze")
def analyze_document(
    document_id: int, 
    request: AnalysisRequest = None,
    db: Session = Depends(get_db)
):
    """
    Trigger analysis for a specific document.
    
    Args:
        document_id: ID of the document to analyze
        request: Optional analysis request with custom prompt
        db: Database session
        
    Returns:
        Success message
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status not in [DocumentStatus.SCRAPED, DocumentStatus.ANALYZED]:
        raise HTTPException(
            status_code=400, 
            detail="Document must be scraped before analysis"
        )
    
    try:
        analyzer = DocumentAnalyzer()
        custom_prompt = request.custom_prompt if request else None
        
        success = analyzer.analyze_document(document, db, custom_prompt)
        
        if success:
            return {"message": f"Analysis started for document: {document.title}"}
        else:
            raise HTTPException(status_code=500, detail="Analysis failed")
            
    except Exception as e:
        logger.error(f"Error analyzing document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error during analysis") 