#!/usr/bin/env python3
"""Test script to check Pinecone data and search functionality"""

import requests
import json

def test_pinecone_search():
    """Test the real Pinecone search functionality"""
    
    # Test sync first to ensure data exists
    print("🔄 Triggering content sync...")
    try:
        sync_response = requests.post('http://localhost:5000/sync', timeout=30)
        print(f"Sync Status: {sync_response.status_code}")
        if sync_response.status_code == 200:
            sync_data = sync_response.json()
            print(f"✅ Sync successful: {sync_data}")
        else:
            print(f"⚠️ Sync response: {sync_response.text}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    
    print("\n" + "="*50)
    
    # Test search with real query
    search_queries = [
        "red sneakers",
        "wireless headphones", 
        "comfortable shoes",
        "gym workout gear"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Testing search: '{query}'")
        try:
            search_response = requests.post(
                'http://localhost:5000/search',
                json={'query': query, 'top_k': 5},
                timeout=15
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search successful!")
                print(f"📝 Expanded queries: {results.get('expanded_queries', [])}")
                print(f"🎯 Found {len(results.get('results', []))} results:")
                
                for i, result in enumerate(results.get('results', [])[:3]):
                    print(f"  {i+1}. {result.get('title', result.get('name', 'Unknown'))}")
                    print(f"     Score: {result.get('score', 0):.3f}")
                    print(f"     Description: {result.get('description', 'No description')[:100]}...")
                    print()
                    
            else:
                print(f"❌ Search failed: {search_response.status_code}")
                print(f"Error: {search_response.text}")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    # Test health check
    print("\n" + "="*50)
    print("🏥 Testing health check...")
    try:
        health_response = requests.get('http://localhost:5000/health', timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check: {health_data}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🚀 Testing REAL Pinecone Search with Contentstack Data")
    print("="*60)
    test_pinecone_search()
    print("\n🏁 Test complete!")