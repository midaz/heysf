#!/usr/bin/env python3
"""Test full LLM analysis with improved PDF extraction."""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_full_analysis():
    print("🤖 Testing Full LLM Analysis Pipeline...")
    
    try:
        from app.database import get_db
        from app.models import Document, DocumentStatus
        from app.services.analyzer import DocumentAnalyzer
        
        # Get a scraped document  
        db = next(get_db())
        doc = db.query(Document).filter(Document.status == DocumentStatus.SCRAPED).first()
        
        if doc:
            print(f"📄 Testing analysis on: {doc.title}")
            print(f"🔗 URL: {doc.url}")
            
            analyzer = DocumentAnalyzer()
            success = analyzer.analyze_document(doc, db)
            
            print(f"✅ Analysis result: {'SUCCESS' if success else 'FAILED'}")
            if success:
                print(f"📊 Document status: {doc.status}")
                
                # Try to get the analysis result
                from app.models import Analysis
                analysis = db.query(Analysis).filter(Analysis.document_id == doc.id).first()
                if analysis:
                    print(f"📝 Analysis preview: {analysis.result[:300]}...")
                else:
                    print("⚠️ No analysis record found")
            else:
                print("❌ Analysis failed")
        else:
            print("❌ No scraped documents found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_full_analysis() 