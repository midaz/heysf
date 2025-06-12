#!/usr/bin/env python3
"""Test script for PDF text extraction."""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_pdf_extraction():
    print("🔍 Testing PDF Text Extraction...")
    
    try:
        from app.database import get_db
        from app.models import Document, DocumentStatus
        from app.services.scraper import SFBOSScraper
        
        # Get a document that was scraped (likely PDF)
        db = next(get_db())
        scraped_docs = db.query(Document).filter(
            Document.status == DocumentStatus.SCRAPED
        ).limit(3).all()
        
        if not scraped_docs:
            print("   ❌ No scraped documents found to test")
            return
        
        scraper = SFBOSScraper()
        
        for doc in scraped_docs:
            print(f"\n📄 Testing document: {doc.title}")
            print(f"   🔗 URL: {doc.url}")
            
            # Try to extract content with new PDF extraction
            content = scraper.download_document_content(doc.url)
            
            if content:
                print(f"   ✅ Content extracted: {len(content)} characters")
                print(f"   📝 Preview: {content[:200]}...")
                
                # Check if this looks like readable text (not PDF binary)
                if content.startswith('%PDF'):
                    print("   ⚠️  Still getting PDF binary - might need different approach")
                else:
                    print("   🎉 Success! Extracted readable text content")
                    
                    # Test if this would work with LLM
                    if len(content) > 100 and any(word in content.lower() for word in ['board', 'meeting', 'supervisor']):
                        print("   🤖 Content looks suitable for LLM analysis")
                    else:
                        print("   ⚠️  Content might not be meeting minutes")
                        
            else:
                print("   ❌ Failed to extract content")
                
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

if __name__ == "__main__":
    test_pdf_extraction() 