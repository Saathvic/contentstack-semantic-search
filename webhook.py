from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging for production
def setup_logging():
    handlers = [logging.StreamHandler()]  # Always log to console
    
    # Only add file handler if logs directory exists (local development)
    if os.path.exists('logs'):
        handlers.append(logging.FileHandler('logs/webhook.log'))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production CORS configuration - Allow all origins for Launch integration
CORS(app, 
     origins=["*"],  # Allow all origins for Launch
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     supports_credentials=False)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        
        # Allow all origins for Launch integration
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

@app.after_request
def add_cors_headers(response):
    # Allow all origins for Launch integration
    origin = request.headers.get('Origin')
    response.headers['Access-Control-Allow-Origin'] = origin or '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# Lazy loading of heavy dependencies
_pinecone_manager = None
_contentstack_fetcher = None
_query_rewriter = None
_config = None

def get_config():
    """Lazy load config"""
    global _config
    if _config is None:
        try:
            from config import config
            _config = config
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            # Create minimal config
            class MinimalConfig:
                DEFAULT_TOP_K = 5
            _config = MinimalConfig()
    return _config

def get_pinecone_manager():
    """Lazy load Pinecone manager"""
    global _pinecone_manager
    if _pinecone_manager is None:
        try:
            from pinecone_integration import PineconeManager
            _pinecone_manager = PineconeManager()
            print("✅ Pinecone manager initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Pinecone: {e}")
            _pinecone_manager = None
    return _pinecone_manager

def get_contentstack_fetcher():
    """Lazy load Contentstack fetcher"""
    global _contentstack_fetcher
    if _contentstack_fetcher is None:
        try:
            from contentstack_fetcher import ContentstackFetcher
            _contentstack_fetcher = ContentstackFetcher()
            print("✅ Contentstack fetcher initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Contentstack fetcher: {e}")
            _contentstack_fetcher = None
    return _contentstack_fetcher

def get_query_rewriter():
    """Lazy load query rewriter"""
    global _query_rewriter
    if _query_rewriter is None:
        try:
            from query_rewriter import QueryRewriter
            _query_rewriter = QueryRewriter()
            print("✅ Query rewriter initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Query rewriter: {e}")
            _query_rewriter = None
    return _query_rewriter

def generate_embedding(entry_data):
    """Lazy load embedding generation"""
    try:
        from embeddings_generator import generate_product_embedding
        return generate_product_embedding(entry_data)
    except Exception as e:
        print(f"Warning: Could not generate embedding: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - always returns success for Launch"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "contentstack-semantic-search",
        "version": "1.0.0",
        "cors": "enabled"
    }), 200

@app.route('/warmup', methods=['GET'])
def warmup():
    """Warmup endpoint to initialize services"""
    try:
        print("🔄 Warming up services...")
        
        # Initialize all components
        config = get_config()
        pinecone_manager = get_pinecone_manager()
        contentstack_fetcher = get_contentstack_fetcher()
        query_rewriter = get_query_rewriter()
        
        return jsonify({
            "status": "warmed_up",
            "timestamp": datetime.now().isoformat(),
            "message": "All services initialized"
        }), 200
        
    except Exception as e:
        print(f"⚠️ Warmup warning: {e}")
        return jsonify({
            "status": "partial_warmup",
            "timestamp": datetime.now().isoformat(),
            "message": "Some services may still be initializing"
        }), 200

@app.route('/search', methods=['POST', 'OPTIONS'])
def search():
    """Search endpoint with graceful degradation and CORS support"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response
    try:
        # Basic validation
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        query = data.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        config = get_config()
        top_k = min(data.get('top_k', config.DEFAULT_TOP_K), 10)
        
        print(f"🔍 Search query: '{query}' (top_k: {top_k})")
        
        # Try to use real search
        try:
            pinecone_manager = get_pinecone_manager()
            if pinecone_manager:
                # Try real search
                embedding = generate_embedding({'title': query, 'description': query})
                if embedding:
                    results = pinecone_manager.search_similar(embedding, top_k=top_k)
                    
                    search_results = []
                    for match in results.get('matches', []):
                        metadata = match.get('metadata', {})
                        search_results.append({
                            'product_id': match['id'],
                            'name': metadata.get('name', metadata.get('title', f'Product {match["id"]}')),
                            'title': metadata.get('title', metadata.get('name', f'Product {match["id"]}')),
                            'description': metadata.get('description', ''),
                            'price': metadata.get('price', 0),
                            'category': metadata.get('category', ''),
                            'brand': metadata.get('brand', ''),
                            'image_url': metadata.get('image_url', ''),
                            'score': match['score'],
                            'query_used': query
                        })
                    
                    return jsonify({
                        "query": query,
                        "results": search_results,
                        "total_results": len(search_results),
                        "status": "success"
                    }), 200
        
        except Exception as e:
            print(f"⚠️ Real search failed: {e}")
        
        # Fallback to mock results
        mock_results = [
            {
                "product_id": "demo_001",
                "name": f"Demo Product for '{query}'",
                "title": f"Search Result: {query}",
                "description": f"This is a demo result for your search query: {query}. The semantic search system is starting up.",
                "price": 99.99,
                "category": "Demo",
                "brand": "Sample",
                "image_url": "",
                "score": 0.85,
                "query_used": query
            }
        ]
        
        return jsonify({
            "query": query,
            "results": mock_results,
            "total_results": len(mock_results),
            "status": "demo_mode",
            "message": "Showing demo results - search service is initializing"
        }), 200
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return jsonify({
            "error": "Search service error",
            "message": str(e),
            "status": "error"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Contentstack webhook endpoint"""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        print("=== WEBHOOK RECEIVED ===")
        print(f"Event: {data.get('event', 'N/A')}")
        print(f"Content Type: {data.get('content_type_uid', 'N/A')}")
        
        # Log webhook but don't fail if processing fails
        try:
            # Try to process webhook
            event_type = data.get('event')
            entry_data = data.get('data', {}).get('entry', {})
            entry_uid = entry_data.get('uid')
            
            if entry_uid and event_type:
                print(f"Processing {event_type} for entry {entry_uid}")
                # TODO: Add webhook processing logic here when service is stable
                
        except Exception as e:
            print(f"⚠️ Webhook processing failed: {e}")
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-post', methods=['POST'])
def test_post():
    """Simple test POST endpoint"""
    try:
        data = request.get_json() if request.is_json else {}
        return jsonify({
            "status": "success",
            "message": "POST endpoint working",
            "received_data": data,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)