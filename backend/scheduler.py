"""
Background scheduler for document scraping and analysis.
"""
import time
import logging
import schedule
from datetime import datetime

from app.database import SessionLocal
from app.services.scraper import SFBOSScraper
from app.services.analyzer import DocumentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_scraping_and_analysis():
    """
    Run the complete scraping and analysis pipeline.
    """
    logger.info("Starting scheduled scraping and analysis job")
    
    db = SessionLocal()
    
    try:
        # Initialize services
        scraper = SFBOSScraper()
        analyzer = DocumentAnalyzer()
        
        # Step 1: Check for new documents
        logger.info("Checking for new documents...")
        new_documents = scraper.check_for_new_documents(db)
        logger.info(f"Found {len(new_documents)} new documents")
        
        # Step 2: Scrape content for new documents
        scraped_count = 0
        for document in new_documents:
            if scraper.scrape_document(document, db):
                scraped_count += 1
        
        logger.info(f"Successfully scraped {scraped_count} documents")
        
        # Step 3: Analyze all pending documents
        logger.info("Analyzing pending documents...")
        analyzed_count = analyzer.analyze_pending_documents(db)
        logger.info(f"Successfully analyzed {analyzed_count} documents")
        
        logger.info("Scheduled job completed successfully")
        
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}")
        
    finally:
        db.close()


def main():
    """
    Main scheduler function.
    """
    logger.info("Starting SF Document Analysis Scheduler")
    
    # Schedule the job to run daily at 9 AM
    schedule.every().day.at("09:00").do(run_scraping_and_analysis)
    
    # Also schedule it to run every 6 hours for more frequent updates
    schedule.every(6).hours.do(run_scraping_and_analysis)
    
    logger.info("Scheduler started. Jobs scheduled for:")
    logger.info("- Daily at 9:00 AM")
    logger.info("- Every 6 hours")
    
    # Run once immediately to get started
    logger.info("Running initial scraping and analysis...")
    run_scraping_and_analysis()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main() 