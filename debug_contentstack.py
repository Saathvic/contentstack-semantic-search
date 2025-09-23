"""
ContentStack API Credentials Debugging Tool
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_contentstack_credentials():
    """
    Debug ContentStack API credentials and provide guidance
    """
    print("🔍 CONTENTSTACK API CREDENTIALS DEBUG")
    print("=" * 50)
    
    # Load credentials
    api_base_url = os.getenv("CONTENTSTACK_API_BASE_URL", "https://cdn.contentstack.io")
    stack_api_key = os.getenv("CONTENTSTACK_STACK_API_KEY")
    delivery_token = os.getenv("CONTENTSTACK_DELIVERY_TOKEN")
    environment = os.getenv("CONTENTSTACK_ENVIRONMENT")
    
    print("📋 Current Configuration:")
    print(f"   API Base URL: {api_base_url}")
    print(f"   Stack API Key: {stack_api_key}")
    print(f"   Delivery Token: {delivery_token}")
    print(f"   Environment: {environment}")
    
    # Check for missing values
    missing_config = []
    if not stack_api_key:
        missing_config.append("CONTENTSTACK_STACK_API_KEY")
    if not delivery_token:
        missing_config.append("CONTENTSTACK_DELIVERY_TOKEN")
    if not environment:
        missing_config.append("CONTENTSTACK_ENVIRONMENT")
    
    if missing_config:
        print(f"\n❌ Missing configuration: {', '.join(missing_config)}")
        return False
    
    # Validate API key format
    print(f"\n🔍 API Key Analysis:")
    print(f"   Length: {len(stack_api_key)} characters")
    print(f"   Format: {'✅ Starts with blt' if stack_api_key.startswith('blt') else '❌ Should start with blt'}")
    
    # Validate delivery token format
    print(f"\n🔍 Delivery Token Analysis:")
    print(f"   Length: {len(delivery_token)} characters")
    print(f"   Format: {'✅ Starts with cs' if delivery_token.startswith('cs') else '❌ Should start with cs'}")
    
    # Test different API endpoints
    print(f"\n🧪 Testing API Endpoints:")
    
    # Test 1: Basic stack info (no authentication needed)
    test_basic_api(api_base_url)
    
    # Test 2: Stack with credentials
    test_stack_with_credentials(api_base_url, stack_api_key, delivery_token, environment)
    
    # Test 3: Different environments
    test_different_environments(api_base_url, stack_api_key, delivery_token)
    
    return True

def test_basic_api(api_base_url):
    """Test basic API connectivity"""
    print(f"\n1. 🌐 Testing basic API connectivity...")
    try:
        response = requests.get(f"{api_base_url}/v3", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Basic API is reachable")
        else:
            print(f"   ⚠️  Unexpected status: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Basic API test failed: {e}")

def test_stack_with_credentials(api_base_url, stack_api_key, delivery_token, environment):
    """Test stack access with current credentials"""
    print(f"\n2. 🔑 Testing credentials with current environment ({environment})...")
    
    url = f"{api_base_url}/v3/content_types"
    headers = {
        'api_key': stack_api_key,
        'access_token': delivery_token,
        'Content-Type': 'application/json'
    }
    params = {
        'environment': environment
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content_types = data.get('content_types', [])
            print(f"   ✅ Success! Found {len(content_types)} content types")
            for ct in content_types[:5]:  # Show first 5
                print(f"      - {ct.get('uid', 'unknown')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            analyze_error_response(response)
    
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_different_environments(api_base_url, stack_api_key, delivery_token):
    """Test different environments"""
    print(f"\n3. 🔄 Testing different environments...")
    
    environments = ['development', 'staging', 'production', 'dev', 'stage', 'prod', 'live']
    
    for env in environments:
        print(f"   Testing environment: {env}")
        
        url = f"{api_base_url}/v3/content_types"
        headers = {
            'api_key': stack_api_key,
            'access_token': delivery_token,
            'Content-Type': 'application/json'
        }
        params = {
            'environment': env
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                content_types = data.get('content_types', [])
                print(f"      ✅ {env}: Found {len(content_types)} content types")
            elif response.status_code == 422:
                print(f"      ❌ {env}: Environment not found")
            else:
                print(f"      ❌ {env}: Status {response.status_code}")
        except:
            print(f"      ❌ {env}: Request failed")

def analyze_error_response(response):
    """Analyze error response and provide suggestions"""
    try:
        error_data = response.json()
        error_code = error_data.get('error_code')
        error_message = error_data.get('error_message')
        errors = error_data.get('errors', {})
        
        print(f"   🔍 Error Analysis:")
        print(f"      Code: {error_code}")
        print(f"      Message: {error_message}")
        
        if error_code == 109:
            print(f"   💡 Error 109 Suggestions:")
            print(f"      - Verify the Stack API Key is correct")
            print(f"      - Check if you're using the right stack")
            print(f"      - Ensure the API key has proper permissions")
            print(f"      - Try regenerating the API key in ContentStack dashboard")
        
        if 'api_key' in errors:
            print(f"   🔑 API Key Issues:")
            for error in errors['api_key']:
                print(f"      - {error}")
        
        if 'access_token' in errors:
            print(f"   🎫 Access Token Issues:")
            for error in errors['access_token']:
                print(f"      - {error}")
    
    except:
        print(f"   ⚠️  Could not parse error response")

def provide_troubleshooting_guide():
    """Provide step-by-step troubleshooting guide"""
    print(f"\n🛠️  TROUBLESHOOTING GUIDE")
    print("=" * 30)
    
    print("1. 📋 Verify ContentStack Dashboard Settings:")
    print("   - Log into your ContentStack account")
    print("   - Go to Settings > Stack Settings")
    print("   - Copy the Stack API Key (starts with 'blt')")
    
    print("\\n2. 🔑 Check Delivery Tokens:")
    print("   - Go to Settings > Tokens")
    print("   - Find your delivery token (starts with 'cs')")
    print("   - Ensure it's enabled for the correct environment")
    
    print("\\n3. 🌍 Verify Environment:")
    print("   - Check Settings > Environments")
    print("   - Note the exact environment name (case sensitive)")
    print("   - Common names: development, staging, production")
    
    print("\\n4. 🔒 Check Permissions:")
    print("   - Ensure the delivery token has read permissions")
    print("   - Verify no IP restrictions are blocking your requests")
    
    print("\\n5. 📝 Update .env file with correct values:")
    print("   CONTENTSTACK_STACK_API_KEY=your_stack_api_key")
    print("   CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token")
    print("   CONTENTSTACK_ENVIRONMENT=your_environment_name")

if __name__ == "__main__":
    debug_contentstack_credentials()
    provide_troubleshooting_guide()