"""
Main FastAPI application for SF Government Document Analysis.
"""
import logging
from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, engine
from .models import Base, Document, DocumentStatus
from .schemas import HealthResponse
from .routers import documents, analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for analyzing SF government documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(analysis.router)


@app.get("/", response_model=dict)
def root():
    """Root endpoint."""
    return {
        "message": "SF Government Document Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Health status information
    """
    try:
        # Test database connection
        total_documents = db.query(Document).count()
        analyzed_documents = db.query(Document).filter(
            Document.status == DocumentStatus.ANALYZED
        ).count()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            database_connected=True,
            total_documents=total_documents,
            analyzed_documents=analyzed_documents
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            database_connected=False,
            total_documents=0,
            analyzed_documents=0
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 