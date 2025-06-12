#!/usr/bin/env python3
"""Test script for debugging document analysis."""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Test the analysis workflow step by step
def test_analysis():
    print("🔍 Testing SF Document Analysis System...")
    
    # Test 1: Environment variables
    print("\n1. Checking environment variables...")
    openai_key = os.getenv('OPENAI_API_KEY')
    s3_bucket = os.getenv('aws_s3_bucket')
    print(f"   ✅ OpenAI API Key: {'SET' if openai_key else 'MISSING'}")
    print(f"   ✅ S3 Bucket: {s3_bucket if s3_bucket else 'MISSING'}")
    
    # Test 2: Database connection
    print("\n2. Testing database connection...")
    try:
        from app.database import get_db
        from app.models import Document
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        documents = db.query(Document).limit(1).all()
        print(f"   ✅ Database connected. Found {len(documents)} documents")
        
        if documents:
            test_doc = documents[0]
            print(f"   📄 Test document: {test_doc.title}")
            print(f"   📄 Status: {test_doc.status}")
            print(f"   📄 File path: {test_doc.file_path}")
        else:
            print("   ⚠️  No documents found in database")
            return
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Test 3: Document content retrieval
    print("\n3. Testing document content retrieval...")
    try:
        from app.services.analyzer import DocumentAnalyzer
        analyzer = DocumentAnalyzer()
        
        content = analyzer._get_document_content(test_doc)
        if content:
            print(f"   ✅ Content retrieved: {len(content)} characters")
            print(f"   📝 Preview: {content[:100]}...")
        else:
            print("   ❌ Failed to retrieve document content")
            return
            
    except Exception as e:
        print(f"   ❌ Content retrieval error: {e}")
        return
    
    # Test 4: LLM Analysis
    print("\n4. Testing LLM analysis...")
    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage
        
        llm = ChatOpenAI(api_key=openai_key, model="gpt-4", temperature=0.1)
        
        # Simple test prompt
        test_prompt = "Summarize this SF Board of Supervisors meeting in 2 sentences:"
        full_prompt = f"{test_prompt}\n\n{content[:1000]}"  # Use first 1000 chars
        
        response = llm.invoke([HumanMessage(content=full_prompt)])
        print(f"   ✅ LLM Analysis successful!")
        print(f"   📝 Response: {response.content[:200]}...")
        
    except Exception as e:
        print(f"   ❌ LLM Analysis error: {e}")
        return
    
    print("\n🎉 All tests passed! Analysis system is working correctly.")

if __name__ == "__main__":
    test_analysis() 