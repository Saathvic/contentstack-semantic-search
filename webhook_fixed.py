from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from pyngrok import ngrok
import json
import logging
from datetime import datetime
from embeddings_generator import generate_product_embedding
from pinecone_integration import PineconeManager
from contentstack_fetcher import ContentstackFetcher
from query_rewriter import QueryRewriter
from config import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        
        # Allow both localhost, network IP, and the ngrok frontend domain
        allowed_origins = [
            'http://localhost:3000',
            'http://localhost:3001',
            'http://192.168.1.14:3001',
            f'https://{config.NGROK_FRONTEND_DOMAIN}'
        ]
        
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

@app.after_request
def add_cors_headers(response):
    # Allow both localhost, network IP, and the ngrok frontend domain
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://192.168.1.14:3001',
        f'https://{config.NGROK_FRONTEND_DOMAIN}'
    ]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://192.168.1.14:3001"])  # Enable CORS for React dev server

# Global managers
_pinecone_manager = None
_contentstack_fetcher = None
_query_rewriter = None

def get_pinecone_manager():
    """Get or create Pinecone manager"""
    global _pinecone_manager
    if _pinecone_manager is None:
        try:
            _pinecone_manager = PineconeManager()
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            _pinecone_manager = None
    return _pinecone_manager

def get_contentstack_fetcher():
    """Get or create Contentstack fetcher"""
    global _contentstack_fetcher
    if _contentstack_fetcher is None:
        try:
            _contentstack_fetcher = ContentstackFetcher()
        except Exception as e:
            print(f"Failed to initialize Contentstack fetcher: {e}")
            _contentstack_fetcher = None
    return _contentstack_fetcher

def get_query_rewriter():
    """Get or create query rewriter"""
    global _query_rewriter
    if _query_rewriter is None:
        try:
            _query_rewriter = QueryRewriter()
        except Exception as e:
            print(f"Failed to initialize query rewriter: {e}")
            _query_rewriter = None
    return _query_rewriter

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
    entry_data = data.get('data', {}).get('entry', {})
    entry_uid = entry_data.get('uid')
    
    pinecone_manager = get_pinecone_manager()
    
    if event_type in ['entry_published', 'entry_updated', 'entry_created']:
        # Generate embedding and update/add to vector DB/index
        print(f"Action: Entry {entry_uid} needs indexing or update")
        if pinecone_manager and entry_data:
            embedding = generate_product_embedding(entry_data)
            if embedding:
                try:
                    # Prepare metadata
                    metadata = {
                        'entry_uid': entry_uid,
                        'content_type': data.get('content_type_uid'),
                        'event_type': event_type,
                        'title': entry_data.get('title', ''),
                        'locale': entry_data.get('locale', 'en-us')
                    }
                    
                    # Upsert to Pinecone
                    embeddings_dict = {entry_uid: embedding}
                    pinecone_manager.upsert_embeddings(embeddings_dict, metadata)
                    print(f"✅ Successfully indexed entry {entry_uid}")
                except Exception as e:
                    print(f"❌ Error indexing entry {entry_uid}: {e}")
            else:
                print(f"⚠️ No embedding generated for entry {entry_uid}")
        else:
            print(f"📝 Entry {entry_uid} needs indexing (Pinecone not available)")
            
    elif event_type == 'entry_unpublished':
        # Remove from vector DB/index
        print(f"Action: Entry {entry_uid} needs removal from index")
        if pinecone_manager and entry_uid:
            try:
                pinecone_manager.delete_product(entry_uid)
                print(f"🗑️ Successfully removed entry {entry_uid} from index")
            except Exception as e:
                print(f"❌ Error removing entry {entry_uid}: {e}")
        else:
            print(f"📝 Entry {entry_uid} needs removal from index")
            
    elif event_type == 'entry_deleted':
        # Handle deletion
        print(f"Action: Entry {entry_uid} needs permanent removal from index")
        if pinecone_manager and entry_uid:
            try:
                pinecone_manager.delete_product(entry_uid)
                print(f"🗑️ Permanently removed entry {entry_uid} from index")
            except Exception as e:
                print(f"❌ Error permanently removing entry {entry_uid}: {e}")
        else:
            print(f"📝 Entry {entry_uid} needs permanent removal from index")
    else:
        print(f"Unhandled event type: {event_type}")
    
    return jsonify({"status": "success"}), 200

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint for semantic product search"""
    data = request.json
    query = data.get('query', '').strip()
    top_k = data.get('top_k', config.DEFAULT_TOP_K)
    use_rewrite = data.get('rewrite', True)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    print(f"🔍 Search query: '{query}' (top_k: {top_k}, rewrite: {use_rewrite})")
    
    pinecone_manager = get_pinecone_manager()
    if not pinecone_manager:
        return jsonify({"error": "Vector database not available"}), 503
    
    try:
        queries_to_search = [query]  # Always include original
        
        # Expand query if enabled
        if use_rewrite:
            rewriter = get_query_rewriter()
            if rewriter:
                expanded_queries = rewriter.expand_query(query, 3)
                queries_to_search = expanded_queries
                print(f"📝 Expanded to {len(queries_to_search)} queries: {queries_to_search}")
            else:
                print("⚠️ Query rewriter not available, using original query only")
        
        all_results = []
        seen_ids = set()
        
        # Search with each query
        for search_query in queries_to_search:
            query_embedding = generate_product_embedding({'title': search_query, 'description': search_query})
            if not query_embedding:
                continue
                
            results = pinecone_manager.search_similar(query_embedding, top_k=top_k)
            
            for match in results.get('matches', []):
                product_id = match['id']
                if product_id not in seen_ids:
                    all_results.append({
                        'product_id': product_id,
                        'score': match['score'],
                        'metadata': match.get('metadata', {}),
                        'query_used': search_query
                    })
                    seen_ids.add(product_id)
        
        # Sort by score and limit results
        all_results.sort(key=lambda x: x['score'], reverse=True)
        final_results = all_results[:top_k]
        
        print(f"✅ Found {len(final_results)} unique results")
        
        return jsonify({
            "query": query,
            "expanded_queries": queries_to_search if use_rewrite else [query],
            "results": final_results,
            "total_results": len(final_results)
        }), 200
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/sync', methods=['POST'])
def sync_entries():
    """Manually trigger sync of all Contentstack entries to Pinecone"""
    content_type = request.args.get('content_type', 'product')
    
    print(f"🔄 Starting manual sync for content type: {content_type}")
    
    fetcher = get_contentstack_fetcher()
    if not fetcher:
        return jsonify({"error": "Contentstack fetcher not available"}), 503
    
    try:
        fetcher.sync_entries_to_pinecone(content_type)
        return jsonify({"status": "sync_completed", "content_type": content_type}), 200
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    pinecone_status = "available" if get_pinecone_manager() else "unavailable"
    contentstack_status = "available" if get_contentstack_fetcher() else "unavailable"
    rewriter_status = "available" if get_query_rewriter() else "unavailable"

    return jsonify({
        "status": "healthy",
        "services": {
            "pinecone": pinecone_status,
            "contentstack": contentstack_status,
            "query_rewriter": rewriter_status
        },
        "configuration": config.get_status(),
        "ngrok_domain": config.NGROK_WEBHOOK_DOMAIN
    }), 200

if __name__ == "__main__":
    # Start ngrok tunnel with custom domain
    try:
        tunnel = ngrok.connect(5000, domain="destined-mammoth-flowing.ngrok-free.app")
        public_url = tunnel.public_url
        print(f"Ngrok tunnel established: {public_url}")
        print(f"Webhook endpoint: {public_url}/webhook")
    except Exception as e:
        print(f"Failed to establish ngrok tunnel: {e}")
        print("Falling back to local development...")
        public_url = "http://localhost:5000"
    
    print("Starting Flask app...")
    app.run(port=5000)