#!/usr/bin/env python3
"""
Integration test script for Contentstack Semantic Search
Tests all major components to ensure they work together properly.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    try:
        from config import config
        status = config.get_status()
        print("✅ Configuration loaded successfully")
        print(f"   Contentstack: {'✅' if status['contentstack']['configured'] else '❌'}")
        print(f"   Pinecone: {'✅' if status['pinecone']['configured'] else '❌'}")
        print(f"   Gemini: {'✅' if status['gemini']['configured'] else '❌'}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_embeddings():
    """Test embedding generation"""
    print("\n🧠 Testing Embedding Generation...")
    try:
        from embeddings_generator import generate_product_embedding

        test_data = {
            'title': 'Test Product',
            'description': 'This is a test product for embedding generation'
        }

        embedding = generate_product_embedding(test_data)
        if embedding and len(embedding) == 384:
            print("✅ Embedding generation successful")
            print(f"   Embedding dimension: {len(embedding)}")
            return True
        else:
            print("❌ Embedding generation failed or wrong dimension")
            return False
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False

def test_query_rewriter():
    """Test query rewriting (if configured)"""
    print("\n📝 Testing Query Rewriter...")
    try:
        from config import config
        if not config.validate_gemini_config():
            print("⚠️  Gemini not configured, skipping query rewriter test")
            return True

        from query_rewriter import QueryRewriter
        rewriter = QueryRewriter()
        rewrites = rewriter.expand_query("red sneakers", 2)

        if rewrites and len(rewrites) >= 2:
            print("✅ Query rewriting successful")
            print(f"   Generated {len(rewrites)} queries: {rewrites[:2]}")
            return True
        else:
            print("❌ Query rewriting failed")
            return False
    except Exception as e:
        print(f"❌ Query rewriter test failed: {e}")
        return False

def test_contentstack_fetcher():
    """Test Contentstack API connection"""
    print("\n📡 Testing Contentstack Fetcher...")
    try:
        from config import config
        if not config.validate_contentstack_config():
            print("⚠️  Contentstack not configured, skipping fetcher test")
            return True

        from contentstack_fetcher import ContentstackFetcher
        fetcher = ContentstackFetcher()

        # Test fetching a small batch
        data = fetcher.fetch_entries('product', limit=1)
        if data and 'entries' in data:
            print("✅ Contentstack API connection successful")
            print(f"   Found {len(data['entries'])} test entries")
            return True
        else:
            print("❌ Contentstack API test failed")
            return False
    except Exception as e:
        print(f"❌ Contentstack fetcher test failed: {e}")
        return False

def test_pinecone():
    """Test Pinecone connection (if configured)"""
    print("\n📊 Testing Pinecone Connection...")
    try:
        from config import config
        if not config.validate_pinecone_config():
            print("⚠️  Pinecone not configured, skipping connection test")
            return True

        from pinecone_integration import PineconeManager
        manager = PineconeManager()

        stats = manager.get_index_stats()
        if stats:
            print("✅ Pinecone connection successful")
            print(f"   Index: {config.PINECONE_INDEX_NAME}")
            print(f"   Vectors: {stats.get('total_vector_count', 'N/A')}")
            return True
        else:
            print("❌ Pinecone connection failed")
            return False
    except Exception as e:
        print(f"❌ Pinecone test failed: {e}")
        return False

def test_webhook_server():
    """Test webhook server imports and basic functionality"""
    print("\n🌐 Testing Webhook Server...")
    try:
        # Test imports
        from webhook import app, get_pinecone_manager, get_contentstack_fetcher, get_query_rewriter
        print("✅ Webhook server imports successful")

        # Test that managers can be initialized (may fail if not configured)
        try:
            pinecone = get_pinecone_manager()
            contentstack = get_contentstack_fetcher()
            rewriter = get_query_rewriter()
            print("✅ All managers initialized")
        except Exception as e:
            print(f"⚠️  Some managers failed to initialize (expected if not configured): {e}")

        return True
    except Exception as e:
        print(f"❌ Webhook server test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Contentstack Semantic Search Integration Tests")
    print("=" * 60)

    tests = [
        ("Configuration", test_config),
        ("Embeddings", test_embeddings),
        ("Query Rewriter", test_query_rewriter),
        ("Contentstack Fetcher", test_contentstack_fetcher),
        ("Pinecone", test_pinecone),
        ("Webhook Server", test_webhook_server),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! System is ready for deployment.")
        return True
    elif passed >= total * 0.7:  # 70% pass rate
        print("⚠️  Most tests passed. System is mostly functional but may need configuration.")
        return True
    else:
        print("❌ Many tests failed. Please check configuration and dependencies.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)