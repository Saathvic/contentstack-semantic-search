from flask import Flask, request, jsonify
from pyngrok import ngrok
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("=== WEBHOOK TRIGGER RECEIVED ===")
    print(f"Timestamp: {request.headers.get('X-Webhook-Timestamp', 'N/A')}")
    print(f"Event Type: {data.get('event', 'N/A')}")
    print(f"Content Type: {data.get('content_type_uid', 'N/A')}")
    print(f"Entry UID: {data.get('data', {}).get('entry', {}).get('uid', 'N/A')}")
    print("Full Payload:")
    print(json.dumps(data, indent=2))
    print("=================================")
    
    event_type = data.get('event')
    entry_uid = data.get('data', {}).get('entry', {}).get('uid')
    
    if event_type in ['entry_published', 'entry_updated', 'entry_created']:
        # Update or add to vector DB/index
        print(f"Action: Entry {entry_uid} needs indexing or update")
    elif event_type == 'entry_unpublished':
        # Remove from vector DB/index
        print(f"Action: Entry {entry_uid} needs removal from index")
    elif event_type == 'entry_deleted':
        # Handle deletion
        print(f"Action: Entry {entry_uid} needs permanent removal from index")
    else:
        print(f"Unhandled event type: {event_type}")
    
    return jsonify({"status": "success"}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "webhook"}), 200

if __name__ == "__main__":
    # Set ngrok auth token if available
    ngrok_auth_token = os.getenv('NGROK_AUTH_TOKEN')
    if ngrok_auth_token:
        ngrok.set_auth_token(ngrok_auth_token)
        print("Ngrok auth token set successfully")
    else:
        print("Warning: No NGROK_AUTH_TOKEN found in environment")
    
    # Get custom domain from environment
    custom_domain = os.getenv('NGROK_WEBHOOK_DOMAIN', 'destined-mammoth-flowing.ngrok-free.app')
    
    # Start ngrok tunnel with custom domain
    try:
        tunnel = ngrok.connect(5000, domain=custom_domain)
        public_url = tunnel.public_url
        print(f"Ngrok tunnel established: {public_url}")
        print(f"Webhook endpoint: {public_url}/webhook")
        print(f"Health endpoint: {public_url}/health")
    except Exception as e:
        print(f"Failed to establish ngrok tunnel: {e}")
        print("Falling back to local development...")
        public_url = "http://localhost:5000"
        print(f"Local webhook endpoint: {public_url}/webhook")
        print(f"Local health endpoint: {public_url}/health")
    
    print("Starting Flask app...")
    print("Press Ctrl+C to stop the server")
    app.run(port=5000, debug=False)