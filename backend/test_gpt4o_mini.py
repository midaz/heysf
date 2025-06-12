#!/usr/bin/env python3
"""Test GPT-4o-mini with large SF Board of Supervisors documents."""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_gpt4o_mini():
    print("🤖 Testing GPT-4o-mini with Large Documents...")
    
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
            
            # Check if we have content and estimate size
            from app.services.scraper import SFBOSScraper
            scraper = SFBOSScraper()
            content = scraper.download_document_content(doc.url)
            
            if content:
                char_count = len(content)
                token_estimate = char_count // 4  # Rough estimate
                print(f"📊 Content: {char_count:,} characters (~{token_estimate:,} tokens)")
                
                if token_estimate > 100000:  # > 100K tokens might still be too large
                    print("⚠️  Document is very large, might hit context limits")
                else:
                    print("✅ Document size looks good for GPT-4o-mini")
                
                # Test the analysis
                analyzer = DocumentAnalyzer()
                print(f"🔄 Starting analysis with GPT-4o-mini...")
                
                success = analyzer.analyze_document(doc, db)
                
                if success:
                    print("🎉 Analysis completed successfully!")
                    
                    # Check the result
                    from app.models import Analysis
                    analysis = db.query(Analysis).filter(Analysis.document_id == doc.id).first()
                    if analysis:
                        preview = analysis.result[:500] if hasattr(analysis, 'result') else analysis.content[:500]
                        print(f"📝 Analysis preview:\n{preview}...")
                        print(f"📊 Full analysis length: {len(analysis.content):,} characters")
                    else:
                        print("⚠️ Analysis record not found")
                else:
                    print("❌ Analysis failed - check logs for details")
            else:
                print("❌ Could not retrieve document content")
        else:
            print("❌ No scraped documents found")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpt4o_mini() 