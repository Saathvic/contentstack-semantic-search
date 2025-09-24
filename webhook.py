from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import json
import logging
import os
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

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        
        # Allow localhost, network IP, Launch domain, and ngrok frontend domain
        allowed_origins = [
            'http://localhost:3000',
            'http://localhost:3001',
            'http://192.168.1.14:3000',
            'http://192.168.1.14:3001',
            'https://contentstack-semantic-search-71c585.eu-contentstackapps.com',
            f'https://{config.NGROK_FRONTEND_DOMAIN}' if hasattr(config, 'NGROK_FRONTEND_DOMAIN') and config.NGROK_FRONTEND_DOMAIN else None
        ]
        # Remove None values
        allowed_origins = [origin for origin in allowed_origins if origin is not None]
        
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

@app.after_request
def add_cors_headers(response):
    # Allow localhost, network IP, Launch domain, and ngrok frontend domain
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://192.168.1.14:3000',
        'http://192.168.1.14:3001',
        'https://contentstack-semantic-search-71c585.eu-contentstackapps.com',
        f'https://{config.NGROK_FRONTEND_DOMAIN}' if hasattr(config, 'NGROK_FRONTEND_DOMAIN') and config.NGROK_FRONTEND_DOMAIN else None
    ]
    # Remove None values
    allowed_origins = [origin for origin in allowed_origins if origin is not None]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response
# Production CORS configuration
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:3001", 
    "https://contentstack-semantic-search-71c585.eu-contentstackapps.com",
    "https://*.eu-contentstackapps.com",
    "https://*.onrender.com"  # For Render deployment
]

# Add ngrok domain if available (development only)
if hasattr(config, 'NGROK_FRONTEND_DOMAIN') and config.NGROK_FRONTEND_DOMAIN:
    allowed_origins.append(f"https://{config.NGROK_FRONTEND_DOMAIN}")

CORS(app, origins=allowed_origins)

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
                    # Prepare comprehensive metadata with all product details
                    metadata = {
                        'entry_uid': entry_uid,
                        'content_type': data.get('content_type_uid'),
                        'event_type': event_type,
                        'title': entry_data.get('title', ''),
                        'name': entry_data.get('name', entry_data.get('title', '')),
                        'description': entry_data.get('description', ''),
                        'price': entry_data.get('price', 0),
                        'category': entry_data.get('category', ''),
                        'brand': entry_data.get('brand', ''),
                        'image_url': entry_data.get('image', {}).get('url', '') if isinstance(entry_data.get('image'), dict) else '',
                        'locale': entry_data.get('locale', 'en-us'),
                        'created_at': entry_data.get('created_at', ''),
                        'updated_at': entry_data.get('updated_at', '')
                    }
                    
                    # Upsert to Pinecone with complete metadata
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

@app.route('/test-post', methods=['POST'])
def test_post():
    """Simple test POST endpoint to debug POST request issues"""
    try:
        data = request.json if request.is_json else {}
        return jsonify({
            "status": "success",
            "message": "POST endpoint working",
            "received_data": data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
                    metadata = match.get('metadata', {})
                    all_results.append({
                        'product_id': product_id,
                        'name': metadata.get('name', metadata.get('title', f'Product {product_id}')),
                        'title': metadata.get('title', metadata.get('name', f'Product {product_id}')),
                        'description': metadata.get('description', ''),
                        'price': metadata.get('price', 0),
                        'category': metadata.get('category', ''),
                        'brand': metadata.get('brand', ''),
                        'image_url': metadata.get('image_url', ''),
                        'score': match['score'],
                        'metadata': metadata,
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
        "ngrok_domain": config.NGROK_DOMAIN
    }), 200

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve_react_app(path):
#     """Serve React app for all non-API routes"""
#     if path.startswith('api/') or path in ['webhook', 'search', 'sync', 'health']:
#         # Let Flask handle API routes
#         return "Not found", 404
    
#     # Serve React app
#     if path == '' or path == 'index.html':
#         return send_from_directory('contentstack-demo/build', 'index.html')
#     else:
#         return send_from_directory('contentstack-demo/build', path)

if __name__ == '__main__':
    # Initialize global managers
    get_pinecone_manager()
    get_query_rewriter()
    get_contentstack_fetcher()
    
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', config.FLASK_PORT))
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if is_production:
        logger.info("🚀 Starting Contentstack Semantic Search API (Production)...")
        logger.info(f"🌐 Server will be available on port {port}")
        logger.info("🔍 Search API: /search")
        logger.info("🔄 Sync API: /sync") 
        logger.info("🏥 Health check: /health")
        logger.info("📡 Webhook endpoint: /webhook")
    else:
        logger.info("🚀 Starting Contentstack Webhook Server (Development)...")
        
        # Setup ngrok tunnel if configured (development only)
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(config.NGROK_AUTH_TOKEN)
            tunnel = ngrok.connect(port, domain=config.NGROK_WEBHOOK_DOMAIN)
            public_url = tunnel.public_url
            logger.info(f"🌍 Ngrok tunnel established: {public_url}")
            logger.info(f"🎯 Webhook endpoint: {public_url}/webhook")
            logger.info(f"🏥 Health check: {public_url}/health")
            logger.info(f"🔍 Search API: {public_url}/search")
            logger.info(f"🔄 Sync API: {public_url}/sync")
        except Exception as e:
            logger.error(f"❌ Failed to establish ngrok tunnel: {e}")
            logger.info("🔄 Falling back to local development...")
            logger.warning("⚠️ Webhooks will NOT work without ngrok tunnel!")
    
    try:
        if is_production:
            # In production, Gunicorn will handle the WSGI server
            logger.info("✅ Application ready for Gunicorn")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=not is_production
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        logger.info("👋 Goodbye!")
