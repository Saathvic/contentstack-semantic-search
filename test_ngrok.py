#!/usr/bin/env python3
"""
Simple ngrok test script to verify authentication and domain connection
"""
import os
from pyngrok import ngrok, conf
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

def test_ngrok():
    # Load environment variables
    auth_token = os.getenv('NGROK_AUTH_TOKEN')
    domain = os.getenv('NGROK_DOMAIN', 'destined-mammoth-flowing.ngrok-free.app')

    if not auth_token:
        print("❌ NGROK_AUTH_TOKEN not found in environment variables")
        return False

    print(f"🔑 Found auth token: {auth_token[:10]}...")
    print(f"🌐 Target domain: {domain}")

    try:
        # Configure ngrok
        conf.get_default().auth_token = auth_token

        # Test connection
        print("🔄 Testing ngrok connection...")
        tunnel = ngrok.connect(5000, domain=domain)

        print("✅ Ngrok tunnel established successfully!")
        print(f"🌐 Public URL: {tunnel.public_url}")
        print(f"🎯 Webhook endpoint: {tunnel.public_url}/webhook")

        # Keep it alive briefly
        input("Press Enter to close the tunnel...")

        # Close tunnel
        ngrok.disconnect(tunnel.public_url)
        print("🔌 Tunnel closed")

        return True

    except Exception as e:
        print(f"❌ Ngrok connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ngrok()
    sys.exit(0 if success else 1)