"""
Advanced ContentStack API Debugging - Alternative Authentication Methods
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_contentstack_authentication_methods():
    """
    Test different authentication methods and API formats for ContentStack
    """
    print("🔍 ADVANCED CONTENTSTACK API TESTING")
    print("=" * 50)
    
    # Load credentials
    stack_api_key = os.getenv("CONTENTSTACK_STACK_API_KEY")
    delivery_token = os.getenv("CONTENTSTACK_DELIVERY_TOKEN")
    environment = os.getenv("CONTENTSTACK_ENVIRONMENT")
    
    print(f"📋 Using credentials:")
    print(f"   Stack API Key: {stack_api_key}")
    print(f"   Delivery Token: {delivery_token}")
    print(f"   Environment: {environment}")
    
    # Test different authentication methods
    test_methods = [
        {
            "name": "Method 1: Headers + Query Params",
            "headers": {
                'api_key': stack_api_key,
                'access_token': delivery_token,
                'Content-Type': 'application/json'
            },
            "params": {'environment': environment}
        },
        {
            "name": "Method 2: All in Headers",
            "headers": {
                'api_key': stack_api_key,
                'access_token': delivery_token,
                'environment': environment,
                'Content-Type': 'application/json'
            },
            "params": {}
        },
        {
            "name": "Method 3: Authorization Header",
            "headers": {
                'Authorization': f'Bearer {delivery_token}',
                'api_key': stack_api_key,
                'Content-Type': 'application/json'
            },
            "params": {'environment': environment}
        },
        {
            "name": "Method 4: Query Parameters Only",
            "headers": {'Content-Type': 'application/json'},
            "params": {
                'api_key': stack_api_key,
                'access_token': delivery_token,
                'environment': environment
            }
        }
    ]
    
    base_urls = [
        "https://cdn.contentstack.io",
        "https://api.contentstack.io",
        "https://delivery-api.contentstack.io"
    ]
    
    # Test each combination
    for base_url in base_urls:
        print(f"\\n🌐 Testing Base URL: {base_url}")
        
        for method in test_methods:
            print(f"\\n   {method['name']}")
            test_api_method(base_url, method['headers'], method['params'])

def test_api_method(base_url, headers, params):
    """Test specific API method"""
    url = f"{base_url}/v3/content_types"
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                content_types = data.get('content_types', [])
                print(f"      ✅ SUCCESS! Found {len(content_types)} content types")
                if content_types:
                    print(f"         Content types: {[ct.get('uid') for ct in content_types[:3]]}")
                return True
            except:
                print(f"      ✅ SUCCESS! (Response not JSON)")
                return True
        elif response.status_code == 401:
            print(f"      ❌ Unauthorized - Check credentials")
        elif response.status_code == 403:
            print(f"      ❌ Forbidden - Check permissions")
        elif response.status_code == 404:
            print(f"      ❌ Not Found - Wrong endpoint")
        elif response.status_code == 412:
            error_data = response.json()
            print(f"      ❌ Precondition Failed - {error_data.get('error_message', 'Unknown error')}")
        else:
            print(f"      ❌ Error {response.status_code}: {response.text[:100]}")
    
    except Exception as e:
        print(f"      ❌ Request failed: {e}")
    
    return False

def test_stack_validation():
    """
    Test if the stack actually exists with a simpler approach
    """
    print(f"\\n🔍 STACK VALIDATION TEST")
    print("=" * 30)
    
    stack_api_key = os.getenv("CONTENTSTACK_STACK_API_KEY")
    
    # Try to get stack information directly
    url = f"https://api.contentstack.io/v3/stacks"
    headers = {
        'api_key': stack_api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"Testing stack existence with management API...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Stack exists and API key is valid!")
            data = response.json()
            stack = data.get('stack', {})
            print(f"Stack Name: {stack.get('name', 'Unknown')}")
            print(f"Stack UID: {stack.get('uid', 'Unknown')}")
        else:
            print(f"❌ Stack validation failed: {response.text}")
    
    except Exception as e:
        print(f"❌ Stack validation error: {e}")

def create_test_with_known_good_stack():
    """
    Test with ContentStack's demo/public stack if available
    """
    print(f"\\n🧪 TESTING WITH DEMO CREDENTIALS")
    print("=" * 40)
    
    # These are example credentials - replace with known working ones if available
    demo_configs = [
        {
            "name": "Demo Config 1",
            "api_key": "bltxxxxxxxxxxxxxxxxxxx",  # Replace with working demo key
            "access_token": "csxxxxxxxxxxxxxxxxxx",  # Replace with working demo token
            "environment": "production"
        }
    ]
    
    print("ℹ️  Testing with demo credentials to verify API format...")
    print("   (This helps confirm if the issue is credentials vs. API format)")

if __name__ == "__main__":
    test_contentstack_authentication_methods()
    test_stack_validation()
    create_test_with_known_good_stack()
    
    print(f"\\n💡 RECOMMENDATIONS:")
    print("1. Double-check that you copied the credentials from the correct ContentStack account")
    print("2. Verify that you're logged into the right organization/workspace in ContentStack")
    print("3. Try regenerating the delivery token in ContentStack dashboard")
    print("4. Check if there are any IP restrictions on the token")
    print("5. Ensure the stack hasn't been deleted or moved to a different organization")