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
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "webhook_url": "https://destined-mammoth-flowing.ngrok-free.app/webhook",
        "message": "Webhook server is running"
    }), 200

if __name__ == "__main__":
    # Start ngrok tunnel with custom domain
    try:
        tunnel = ngrok.connect(5000, domain="destined-mammoth-flowing.ngrok-free.app")
        public_url = tunnel.public_url
        print(f"Ngrok tunnel established: {public_url}")
        print(f"Webhook endpoint: {public_url}/webhook")
        print(f"Health check: {public_url}/health")
        print("")
        print("🎯 FOR CONTENTSTACK WEBHOOK SETUP:")
        print(f"   URL: {public_url}/webhook")
        print("   Method: POST")
        print("   Content-Type: application/json")
        print("   Enable: Send Content in Payload")
        print("   Events: entry_published, entry_updated, entry_created, entry_unpublished, entry_deleted")
        print("")
    except Exception as e:
        print(f"Failed to establish ngrok tunnel: {e}")
        print("Falling back to local development...")
        print("Webhook will be available at: http://localhost:5000/webhook")
        print("Note: Contentstack webhooks require HTTPS - use ngrok!")
    
    print("Starting Flask app...")
    app.run(port=5000, debug=True)