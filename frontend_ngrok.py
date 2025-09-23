#!/usr/bin/env python3
"""
Separate ngrok server for frontend-backend communication
This runs on a different port and uses the new ngrok domain
"""

import os
from pyngrok import ngrok, conf
from config import config
import time

def start_frontend_ngrok():
    """Start ngrok tunnel for frontend-backend communication"""
    try:
        # Configure ngrok with the frontend auth token
        auth_token = config.NGROK_FRONTEND_AUTH_TOKEN
        if auth_token:
            conf.get_default().auth_token = auth_token
            print("🔑 Frontend ngrok authenticated with token")
        else:
            print("⚠️ No NGROK_FRONTEND_AUTH_TOKEN found")
            return None

        # Start tunnel on port 5000 with the frontend domain
        tunnel = ngrok.connect(5000, domain=config.NGROK_FRONTEND_DOMAIN)
        public_url = tunnel.public_url
        
        print(f"✅ Frontend ngrok tunnel established: {public_url}")
        print(f"🎯 API endpoint: {public_url}/search")
        print(f"🏥 Health check: {public_url}/health")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Failed to establish frontend ngrok tunnel: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting frontend ngrok tunnel...")
    
    tunnel_url = start_frontend_ngrok()
    
    if tunnel_url:
        print(f"📡 Frontend tunnel ready at: {tunnel_url}")
        print("💡 Now start your Flask server with: python webhook.py")
        print("⭐ Configure your React app to use this URL")
        
        # Keep the tunnel alive
        try:
            while True:
                time.sleep(60)
                print("🔄 Tunnel is active...")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down frontend ngrok tunnel")
            ngrok.disconnect(tunnel_url)
            ngrok.kill()
    else:
        print("❌ Failed to start frontend tunnel")