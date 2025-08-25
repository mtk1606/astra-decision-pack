#!/usr/bin/env python3
"""
Test script to verify Pinecone and FAISS setup
"""

import os
import sys
from pathlib import Path

def test_openai():
    """Test OpenAI API connection"""
    print("🔍 Testing OpenAI connection...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.embeddings.create(
            model='text-embedding-3-small', 
            input=['test']
        )
        print("✅ OpenAI connection working!")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def test_pinecone():
    """Test Pinecone connection"""
    print("🔍 Testing Pinecone connection...")
    try:
        import pinecone
        api_key = os.environ.get('PINECONE_API_KEY')
        env = os.environ.get('PINECONE_ENV')
        
        if not api_key or not env:
            print("⚠️  Pinecone credentials not set, skipping test")
            return None
            
        pinecone.init(api_key=api_key, environment=env)
        index = pinecone.Index('astra-signals-dev')
        
        # Test with dummy vector
        test_vector = [0.1] * 1536
        index.upsert(vectors=[('test', test_vector, {'text': 'test'})])
        print("✅ Pinecone connection working!")
        return True
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def test_faiss():
    """Test FAISS fallback"""
    print("🔍 Testing FAISS fallback...")
    try:
        from pinecone_helper import get_store
        
        # This should use FAISS if Pinecone is not available
        store = get_store(embed_dim=1536)
        
        # Test with dummy vectors
        test_vectors = [
            ("doc1", [0.1] * 1536, {"text": "test document 1"}),
            ("doc2", [0.2] * 1536, {"text": "test document 2"})
        ]
        
        store.upsert(test_vectors)
        results = store.query([0.1] * 1536, top_k=2)
        
        print("✅ FAISS fallback working!")
        return True
    except Exception as e:
        print(f"❌ FAISS fallback failed: {e}")
        return False

def test_generate_pack():
    """Test Decision Pack generation"""
    print("🔍 Testing Decision Pack generation...")
    try:
        from generate_pack import generate_pack_for_run
        
        # Create test signals file
        test_signals = {
            "domain": "test.com",
            "signals": {
                "headlines_paragraphs": [
                    "This is a test headline with enough words to generate embeddings",
                    "Another test headline for the growth experiment testing"
                ]
            },
            "timestamp": "2024-01-01T00:00:00+00:00"
        }
        
        import json
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_signals, f)
            test_file = f.name
        
        try:
            result = generate_pack_for_run(test_file)
            
            if result and "pack" in result:
                pack = result["pack"]
                required_keys = [
                    "title", "hypothesis", "expected_lift", "confidence",
                    "confidence_justification", "risks", "assets_needed", "suggested_execution_steps"
                ]
                
                missing_keys = [key for key in required_keys if key not in pack]
                if not missing_keys:
                    print("✅ Decision Pack generation working!")
                    return True
                else:
                    print(f"❌ Missing keys in Decision Pack: {missing_keys}")
                    return False
            else:
                print("❌ Decision Pack generation failed - no result")
                return False
                
        finally:
            os.unlink(test_file)
            
    except Exception as e:
        print(f"❌ Decision Pack generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 GrowthSignal RAG Setup Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("generate_pack.py").exists():
        print("❌ Error: generate_pack.py not found. Please run from rfg/ directory.")
        sys.exit(1)
    
    results = {}
    
    # Test OpenAI
    results['openai'] = test_openai()
    
    # Test Pinecone
    results['pinecone'] = test_pinecone()
    
    # Test FAISS
    results['faiss'] = test_faiss()
    
    # Test Decision Pack generation
    results['generate_pack'] = test_generate_pack()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{test_name:15} {status}")
    
    # Overall status
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the setup instructions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
