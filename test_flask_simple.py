from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)

# Enable CORS for localhost testing
CORS(app, origins=[
    "http://localhost:3000", 
    "http://localhost:3001",
    "https://contentstack-semantic-search-71c585.eu-contentstackapps.com"
])

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Flask server is running!'
    })

@app.route('/search', methods=['POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        return '', 200
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Mock search results for testing
        mock_results = [
            {
                "title": "Red High-Top Sneakers",
                "description": "Comfortable red sneakers with white stripes, perfect for casual wear and light workouts.",
                "price": "$89.99",
                "image_url": "https://via.placeholder.com/200x200/FF4444/FFFFFF?text=Red+Sneakers",
                "score": 0.95
            },
            {
                "title": "Crimson Athletic Shoes",
                "description": "Premium red athletic footwear designed for performance and style.",
                "price": "$124.99", 
                "image_url": "https://via.placeholder.com/200x200/DC143C/FFFFFF?text=Athletic+Shoes",
                "score": 0.88
            },
            {
                "title": "Ruby Sport Trainers",
                "description": "Lightweight red trainers ideal for gym workouts and running.",
                "price": "$99.99",
                "image_url": "https://via.placeholder.com/200x200/8B0000/FFFFFF?text=Trainers",
                "score": 0.82
            }
        ]
        
        # Mock expanded queries
        expanded_queries = [
            f"Original: {query}",
            "Expanded: red athletic footwear",
            "Expanded: crimson sneakers", 
            "Expanded: scarlet sports shoes"
        ]
        
        return jsonify({
            'success': True,
            'results': mock_results,
            'expanded_queries': expanded_queries,
            'total_results': len(mock_results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/sync', methods=['POST'])
def sync_content():
    return jsonify({
        'success': True,
        'message': 'Content sync completed!',
        'synced_entries': 15
    })

if __name__ == '__main__':
    print("🚀 Starting Flask server for local testing...")
    print("🌐 Frontend: http://localhost:3000")
    print("🔍 Search API: http://localhost:5000/search")
    print("🏥 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True)