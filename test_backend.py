import requests
import json
import time

# Test configuration
BASE_URL = "https://contentstack-semantic-search-0qhl.onrender.com"
HEADERS = {
    'Content-Type': 'application/json',
    'Origin': 'https://contentstack-semantic-search-71c585.eu-contentstackapps.com'
}

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            
            if 'components' in data:
                print("   Components:")
                for name, info in data['components'].items():
                    print(f"     - {name}: {info.get('status', 'N/A')}")
            
            print("   ✅ Health endpoint working!")
            return True
        else:
            print(f"   ❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏰ Health endpoint timed out (this might be a cold start)")
        return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False

def test_search_endpoint():
    """Test the search endpoint"""
    print("\n🔍 Testing Search Endpoint...")
    
    test_queries = [
        {"query": "red shoes", "top_k": 3},
        {"query": "blue jacket", "top_k": 2},
        {"query": "electronics", "top_k": 5}
    ]
    
    for i, test_data in enumerate(test_queries, 1):
        print(f"\n   Test {i}: Searching for '{test_data['query']}'...")
        try:
            response = requests.post(
                f"{BASE_URL}/search", 
                json=test_data,
                headers=HEADERS,
                timeout=45
            )
            
            print(f"   Status Code: {response.status_code}")
            
            # Check CORS headers
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            print(f"   CORS Header: {cors_header}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Query: {data.get('query', 'N/A')}")
                print(f"   Results Count: {data.get('total_results', 0)}")
                print(f"   Status: {data.get('status', 'N/A')}")
                
                if data.get('results') and len(data['results']) > 0:
                    first_result = data['results'][0]
                    print(f"   First Result: {first_result.get('title', 'N/A')}")
                    print(f"   Score: {first_result.get('score', 'N/A')}")
                
                if data.get('message'):
                    print(f"   Message: {data['message']}")
                
                print(f"   ✅ Search test {i} passed!")
            else:
                print(f"   ❌ Search test {i} failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Search test {i} timed out")
        except Exception as e:
            print(f"   ❌ Search test {i} error: {e}")

def test_webhook_endpoint():
    """Test the webhook endpoint"""
    print("\n🔍 Testing Webhook Endpoint...")
    
    webhook_data = {
        "event": "entry.create",
        "content_type_uid": "product",
        "data": {
            "entry": {
                "uid": "test_entry_123",
                "title": "Test Product",
                "description": "This is a test product entry"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=webhook_data,
            headers=HEADERS,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ Webhook endpoint working!")
        else:
            print(f"   ❌ Webhook failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Webhook error: {e}")

def main():
    print("🚀 Starting Backend API Tests")
    print(f"Testing: {BASE_URL}")
    print("=" * 50)
    
    # Wait for service to be ready
    print("⏳ Waiting for service to warm up...")
    time.sleep(5)
    
    # Run tests
    health_ok = test_health_endpoint()
    test_search_endpoint()
    test_webhook_endpoint()
    
    print("\n" + "=" * 50)
    if health_ok:
        print("🎉 Backend API tests completed! Service is working.")
    else:
        print("⚠️  Backend API tests completed with some issues.")
    print("🌐 Ready for Launch frontend integration!")

if __name__ == "__main__":
    main()