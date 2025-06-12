#!/usr/bin/env python3
"""Test GPT-4o-mini with multiple SF Board of Supervisors documents."""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def test_multiple_documents():
    print("🔄 Testing GPT-4o-mini with Multiple Documents...")
    
    try:
        from app.database import get_db
        from app.models import Document, DocumentStatus
        from app.services.analyzer import DocumentAnalyzer
        from app.services.scraper import SFBOSScraper
        
        # Get multiple scraped documents  
        db = next(get_db())
        docs = db.query(Document).filter(Document.status == DocumentStatus.SCRAPED).limit(3).all()
        
        if not docs:
            print("❌ No scraped documents found")
            return
        
        print(f"📊 Found {len(docs)} documents to test")
        
        analyzer = DocumentAnalyzer()
        scraper = SFBOSScraper()
        results = []
        
        for i, doc in enumerate(docs, 1):
            print(f"\n📄 Document {i}/{len(docs)}: {doc.title}")
            
            # Get content size
            content = scraper.download_document_content(doc.url)
            if content:
                char_count = len(content)
                token_estimate = char_count // 4
                print(f"   📊 Size: {char_count:,} chars (~{token_estimate:,} tokens)")
                
                # Test analysis
                print(f"   🔄 Analyzing...")
                success = analyzer.analyze_document(doc, db)
                
                if success:
                    # Get analysis result
                    from app.models import Analysis
                    analysis = db.query(Analysis).filter(Analysis.document_id == doc.id).first()
                    
                    result = {
                        'title': doc.title,
                        'char_count': char_count,
                        'token_estimate': token_estimate,
                        'success': True,
                        'analysis_length': len(analysis.content) if analysis else 0
                    }
                    
                    print(f"   ✅ Success! Analysis: {result['analysis_length']:,} chars")
                    if analysis:
                        preview = analysis.content[:150]
                        print(f"   📝 Preview: {preview}...")
                else:
                    result = {
                        'title': doc.title,
                        'char_count': char_count,
                        'token_estimate': token_estimate,
                        'success': False,
                        'analysis_length': 0
                    }
                    print(f"   ❌ Failed")
                
                results.append(result)
            else:
                print(f"   ❌ Could not retrieve content")
        
        # Summary
        print(f"\n📊 **Test Results Summary**")
        print(f"   Total documents tested: {len(results)}")
        successful = [r for r in results if r['success']]
        print(f"   Successful analyses: {len(successful)}/{len(results)}")
        
        if successful:
            avg_chars = sum(r['char_count'] for r in successful) // len(successful)
            avg_tokens = sum(r['token_estimate'] for r in successful) // len(successful)
            avg_analysis = sum(r['analysis_length'] for r in successful) // len(successful)
            
            print(f"   Average document size: {avg_chars:,} chars (~{avg_tokens:,} tokens)")
            print(f"   Average analysis length: {avg_analysis:,} chars")
            
            # Check for consistency
            if len(successful) == len(results):
                print("   🎉 All documents processed successfully!")
                print("   ✅ GPT-4o-mini is working consistently")
            else:
                print(f"   ⚠️  {len(results) - len(successful)} documents failed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multiple_documents() 