"""
Document analysis service using LangChain and OpenAI.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from ..config import settings
from ..models import Document, Analysis, AnalysisType, DocumentStatus
from .storage import S3StorageService
from .scraper import SFBOSScraper

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Service for analyzing documents using LLM."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-4o-mini",  # Higher token limits (200K TPM) and much cheaper
            temperature=0.1  # Low temperature for consistent analysis
        )
        self.storage_service = S3StorageService()
        self.scraper = SFBOSScraper()
    
    def analyze_document(self, document: Document, db: Session, custom_prompt: Optional[str] = None) -> bool:
        """
        Analyze a document using the configured LLM.
        
        Args:
            document: Document to analyze
            db: Database session
            custom_prompt: Optional custom prompt to use instead of default
            
        Returns:
            True if analysis was successful, False otherwise
        """
        try:
            logger.info(f"Starting analysis for document: {document.title}")
            
            # Update document status
            document.status = DocumentStatus.ANALYZING
            db.commit()
            
            # Get document content
            content = self._get_document_content(document)
            if not content:
                logger.error(f"Could not retrieve content for document: {document.title}")
                document.status = DocumentStatus.ERROR
                db.commit()
                return False
            
            # Prepare the prompt
            from ..config import get_custom_prompt
            prompt = custom_prompt if custom_prompt else get_custom_prompt()
            
            # Create the analysis prompt with document content
            full_prompt = f"""
{prompt}

Please analyze the following SF Board of Supervisors meeting minutes:

{content}
"""
            
            # Perform analysis with GPT-4o-mini (high token limits, no chunking needed)
            try:
                response = self.llm.invoke([HumanMessage(content=full_prompt)])
                analysis_content = response.content
                
                if not analysis_content:
                    logger.error(f"Analysis returned empty content for document: {document.title}")
                    document.status = DocumentStatus.ERROR
                    db.commit()
                    return False
                    
            except Exception as e:
                logger.error(f"Error during LLM analysis for document {document.title}: {e}")
                document.status = DocumentStatus.ERROR
                db.commit()
                return False
            
            # Save analysis to database
            analysis = Analysis(
                document_id=document.id,
                analysis_type=AnalysisType.CUSTOM_PROMPT,
                content=analysis_content
            )
            
            db.add(analysis)
            document.status = DocumentStatus.ANALYZED
            db.commit()
            
            logger.info(f"Successfully analyzed document: {document.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing document {document.title}: {e}")
            document.status = DocumentStatus.ERROR
            db.commit()
            return False
    
    def _get_document_content(self, document: Document) -> Optional[str]:
        """
        Get document content either from S3 or by scraping.
        
        Args:
            document: Document to get content for
            
        Returns:
            Document content as string or None if failed
        """
        # First try to get from S3 if file_path exists
        if document.file_path:
            content = self.storage_service.download_text_content(document.file_path)
            if content:
                return content
        
        # If not in S3, scrape the content directly
        logger.info(f"Content not in S3, scraping directly from: {document.url}")
        content = self.scraper.download_document_content(document.url)
        
        # If we got content and don't have a file_path, optionally store in S3
        if content and not document.file_path:
            file_key = f"documents/{document.id}_{document.title.replace(' ', '_')}.txt"
            if self.storage_service.upload_text_content(content, file_key):
                document.file_path = file_key
                # Note: We don't commit here as this is called from within another transaction
        
        return content
    
    def _get_default_prompt(self) -> str:
        """
        Get the default analysis prompt.
        
        Returns:
            Default prompt string
        """
        return """
Please analyze this SF Board of Supervisors meeting minutes and provide:

1. **Executive Summary**: A brief 2-3 sentence overview of the key outcomes of this meeting.

2. **Key Topics Discussed**: List the main agenda items and topics that were discussed.

3. **Decisions Made**: List any votes, resolutions, ordinances, or other decisions that were made.

4. **Action Items**: Extract any follow-up actions, deadlines, or next steps mentioned.

5. **Notable Quotes or Discussions**: Highlight any particularly important statements or debates.

6. **Financial Impact**: Note any budget items, appropriations, or financial decisions.

7. **Public Impact**: Explain how these decisions might affect SF residents.

Please be concise but comprehensive in your analysis.
"""
    
    def analyze_pending_documents(self, db: Session) -> int:
        """
        Analyze all documents that have been scraped but not yet analyzed.
        
        Args:
            db: Database session
            
        Returns:
            Number of documents analyzed
        """
        # Get all scraped documents that haven't been analyzed
        pending_docs = db.query(Document).filter(
            Document.status == DocumentStatus.SCRAPED
        ).all()
        
        analyzed_count = 0
        
        for doc in pending_docs:
            if self.analyze_document(doc, db):
                analyzed_count += 1
            else:
                logger.warning(f"Failed to analyze document: {doc.title}")
        
        logger.info(f"Analyzed {analyzed_count} documents")
        return analyzed_count 