#!/usr/bin/env python3
"""
Webhook ngrok server for Contentstack webhooks
This maintains the original webhook domain for Contentstack integration
"""

import os
from pyngrok import ngrok, conf
from config import config
import time

def start_webhook_ngrok():
    """Start ngrok tunnel for webhook communication"""
    try:
        # Configure ngrok with the original webhook auth token
        auth_token = os.getenv('NGROK_AUTH_TOKEN')
        if auth_token:
            conf.get_default().auth_token = auth_token
            print("🔑 Webhook ngrok authenticated with token")
        else:
            print("⚠️ No NGROK_AUTH_TOKEN found")
            return None

        # Start tunnel on port 5001 with the webhook domain
        tunnel = ngrok.connect(5001, domain=config.NGROK_WEBHOOK_DOMAIN)
        public_url = tunnel.public_url
        
        print(f"✅ Webhook ngrok tunnel established: {public_url}")
        print(f"🎯 Webhook endpoint: {public_url}/webhook")
        print(f"🔄 Sync endpoint: {public_url}/sync")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Failed to establish webhook ngrok tunnel: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting webhook ngrok tunnel...")
    
    tunnel_url = start_webhook_ngrok()
    
    if tunnel_url:
        print(f"📡 Webhook tunnel ready at: {tunnel_url}")
        print("💡 Configure Contentstack webhooks to use this URL")
        print("📝 Webhook URL: {}/webhook".format(tunnel_url))
        
        # Keep the tunnel alive
        try:
            while True:
                time.sleep(60)
                print("🔄 Webhook tunnel is active...")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down webhook ngrok tunnel")
            ngrok.disconnect(tunnel_url)
            ngrok.kill()
    else:
        print("❌ Failed to start webhook tunnel")