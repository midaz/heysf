"""
SF Board of Supervisors document scraper service.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Document, DocumentStatus

logger = logging.getLogger(__name__)


class SFBOSScraper:
    """Scraper for SF Board of Supervisors meeting documents."""
    
    def __init__(self):
        self.base_url = settings.base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SF Document Analysis Bot 1.0'
        })
    
    def get_meeting_minutes_urls(self) -> List[Dict[str, str]]:
        """
        Scrape the main meetings page to get all minutes URLs.
        
        Returns:
            List of dicts with 'title', 'url', and 'date' keys
        """
        meetings_url = f"{self.base_url}/meetings/full-board-meetings"
        
        try:
            response = self.session.get(meetings_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the meetings table
            meetings_table = soup.find('table') or soup.find('div', class_='meetings-table')
            if not meetings_table:
                logger.error("Could not find meetings table on the page")
                return []
            
            documents = []
            
            # Look for rows with minutes links
            rows = meetings_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:  # Date, Agenda, Minutes, Supporting Docs
                    date_cell = cells[0]
                    minutes_cell = cells[2] if len(cells) > 2 else None
                    
                    if minutes_cell:
                        minutes_link = minutes_cell.find('a')
                        if minutes_link and minutes_link.get('href'):
                            # Extract meeting date and title
                            date_text = date_cell.get_text(strip=True)
                            minutes_url = minutes_link.get('href')
                            
                            # Make URL absolute if relative
                            if minutes_url.startswith('/'):
                                minutes_url = f"{self.base_url}{minutes_url}"
                            
                            documents.append({
                                'title': f"Board Meeting Minutes - {date_text}",
                                'url': minutes_url,
                                'date': date_text
                            })
            
            logger.info(f"Found {len(documents)} meeting minutes documents")
            return documents
            
        except requests.RequestException as e:
            logger.error(f"Error fetching meetings page: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing meetings page: {e}")
            return []
    
    def download_document_content(self, url: str) -> Optional[str]:
        """
        Download the content of a document (HTML page).
        
        Args:
            url: URL of the document to download
            
        Returns:
            String content of the document or None if failed
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # For HTML documents, extract the main content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove navigation, scripts, and other non-content elements
            for element in soup(['nav', 'script', 'style', 'header', 'footer']):
                element.decompose()
            
            # Get the main content - look for common content containers
            content_container = (
                soup.find('main') or 
                soup.find('div', class_='content') or 
                soup.find('div', class_='main-content') or
                soup.find('body')
            )
            
            if content_container:
                return content_container.get_text(separator='\n', strip=True)
            else:
                return soup.get_text(separator='\n', strip=True)
                
        except requests.RequestException as e:
            logger.error(f"Error downloading document from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing document content from {url}: {e}")
            return None
    
    def check_for_new_documents(self, db: Session) -> List[Document]:
        """
        Check for new documents that haven't been scraped yet.
        
        Args:
            db: Database session
            
        Returns:
            List of new Document objects created
        """
        # Get all available minutes URLs
        available_docs = self.get_meeting_minutes_urls()
        
        # Get existing document URLs from database
        existing_urls = {doc.url for doc in db.query(Document.url).all()}
        
        new_documents = []
        
        for doc_info in available_docs:
            if doc_info['url'] not in existing_urls:
                # Create new document record
                document = Document(
                    title=doc_info['title'],
                    url=doc_info['url'],
                    status=DocumentStatus.PENDING
                )
                
                db.add(document)
                new_documents.append(document)
                logger.info(f"Added new document: {doc_info['title']}")
        
        if new_documents:
            db.commit()
            logger.info(f"Added {len(new_documents)} new documents to database")
        else:
            logger.info("No new documents found")
        
        return new_documents
    
    def scrape_document(self, document: Document, db: Session) -> bool:
        """
        Scrape content for a specific document.
        
        Args:
            document: Document object to scrape
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Scraping document: {document.title}")
            
            # Update status to indicate scraping in progress
            document.status = DocumentStatus.SCRAPED
            db.commit()
            
            # Download document content
            content = self.download_document_content(document.url)
            
            if content:
                # For now, we'll store content as analysis since we're not using S3 yet
                # In full implementation, this would be uploaded to S3
                document.scraped_at = datetime.utcnow()
                document.status = DocumentStatus.SCRAPED
                db.commit()
                
                logger.info(f"Successfully scraped document: {document.title}")
                return True
            else:
                document.status = DocumentStatus.ERROR
                db.commit()
                logger.error(f"Failed to download content for: {document.title}")
                return False
                
        except Exception as e:
            document.status = DocumentStatus.ERROR
            db.commit()
            logger.error(f"Error scraping document {document.title}: {e}")
            return False 