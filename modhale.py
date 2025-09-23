"""
ContentStack Product Embedding System
Main working file for processing ContentStack products and generating embeddings
Using direct API calls (compatible with Python 3.9)
"""
import os
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
from datetime import datetime
from dotenv import load_dotenv

def main():
    """Main function to run ContentStack embedding system"""
    print("🎯 CONTENTSTACK PRODUCT EMBEDDING SYSTEM")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get ContentStack credentials
    api_key = os.getenv("CONTENTSTACK_STACK_API_KEY")
    delivery_token = os.getenv("CONTENTSTACK_DELIVERY_TOKEN")
    environment = os.getenv("CONTENTSTACK_ENVIRONMENT", "development")
    
    if not api_key or not delivery_token:
        print("❌ ERROR: ContentStack credentials missing!")
        print("Please add the following to your .env file:")
        print("CONTENTSTACK_STACK_API_KEY=your_api_key_here")
        print("CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token_here")
        print("CONTENTSTACK_ENVIRONMENT=your_environment_name_here")
        return
    
    print(f"📋 Using ContentStack configuration:")
    print(f"   API Key: {api_key}")
    print(f"   Delivery Token: {delivery_token}")
    print(f"   Environment: {environment}")
    
    # ContentStack API base URL
    base_url = "https://cdn.contentstack.io/v3"
    
    # Common headers for all requests
    headers = {
        'api_key': api_key,
        'access_token': delivery_token,
        'Content-Type': 'application/json'
    }
    
    try:
        # Initialize embedding model
        print("\n🤖 Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded successfully")
        
        # Test connection by getting content types
        print("\n🔍 Testing ContentStack connection...")
        try:
            url = f"{base_url}/content_types"
            params = {'environment': environment}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                content_types = [ct.get('uid') for ct in data.get('content_types', [])]
                print(f"✅ Connection successful! Found content types: {content_types}")
                
                # Find product content type
                product_type = None
                for ct_name in ['product', 'products', 'Product', 'Products']:
                    if ct_name in content_types:
                        product_type = ct_name
                        break
                
                if not product_type:
                    print("❌ No product content type found!")
                    print(f"Available content types: {content_types}")
                    print("💡 Please create a 'product' content type in ContentStack")
                    return
                
                print(f"✅ Using product content type: {product_type}")
                
            else:
                print(f"❌ ContentStack connection failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error_message', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                print("\n💡 Please check:")
                print("1. Your API key and delivery token are correct")
                print("2. You're using the right environment name")
                print("3. Your credentials have proper permissions")
                return
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return
        
        # Fetch products
        print(f"\n📡 Fetching products from ContentStack...")
        try:
            url = f"{base_url}/content_types/{product_type}/entries"
            params = {
                'environment': environment,
                'include_count': 'true',
                'limit': 50
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('entries', [])
                total_count = data.get('count', len(products))
                
                print(f"✅ Fetched {len(products)} products (Total: {total_count})")
                
                if not products:
                    print("❌ No products found in ContentStack")
                    print("💡 Add some product entries to your ContentStack")
                    return
                
                # Show first product structure
                if products:
                    first_product = products[0]
                    print(f"\n📋 Sample product fields:")
                    for key, value in first_product.items():
                        if key not in ['created_at', 'updated_at', 'created_by', 'updated_by', '_version']:
                            print(f"   - {key}: {type(value).__name__}")
                
            else:
                print(f"❌ Failed to fetch products: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                return
            
        except Exception as e:
            print(f"❌ Error fetching products: {e}")
            return
        
        # Process products and generate embeddings
        print(f"\n📊 Generating embeddings for {len(products)} products...")
        
        results = {
            "source": "contentstack_api",
            "content_type": product_type,
            "embeddings": {},
            "metadata": {},
            "stats": {
                "total_products": len(products),
                "successful_embeddings": 0,
                "failed_embeddings": 0,
                "timestamp": datetime.now().isoformat(),
                "model_used": "all-MiniLM-L6-v2",
                "embedding_dimension": 384
            }
        }
        
        for i, product in enumerate(products, 1):
            uid = product.get('uid', f'product_{i}')
            title = product.get('title', product.get('name', f'Product {i}'))
            
            print(f"   Processing {i}/{len(products)}: {title}")
            
            # Create text for embedding
            text_parts = []
            
            # Extract key fields
            if 'title' in product:
                text_parts.append(str(product['title']))
            if 'description' in product:
                text_parts.append(str(product['description']))
            if 'category' in product:
                text_parts.append(str(product['category']))
            
            # Add other text fields
            skip_fields = ['uid', 'created_at', 'updated_at', 'created_by', 'updated_by', '_version', 'ACL', 'locale']
            for key, value in product.items():
                if key not in skip_fields and key not in ['title', 'description', 'category']:
                    if isinstance(value, str) and value.strip():
                        text_parts.append(value.strip())
                    elif isinstance(value, list):
                        # Handle arrays (like tags, features, etc.)
                        for item in value:
                            if isinstance(item, str) and item.strip():
                                text_parts.append(item.strip())
            
            embedding_text = ' '.join(text_parts).strip()
            
            if not embedding_text:
                embedding_text = f"Product {uid}"
            
            print(f"      Text: {embedding_text[:60]}{'...' if len(embedding_text) > 60 else ''}")
            
            # Generate embedding
            try:
                embedding = model.encode(embedding_text)
                
                results["embeddings"][uid] = embedding.tolist()
                results["metadata"][uid] = {
                    "title": title,
                    "uid": uid,
                    "embedding_text": embedding_text,
                    "embedding_dimension": len(embedding),
                    "processed_at": datetime.now().isoformat(),
                    "contentstack_data": product
                }
                results["stats"]["successful_embeddings"] += 1
                print(f"      ✅ Embedding generated (dimension: {len(embedding)})")
                
            except Exception as e:
                results["stats"]["failed_embeddings"] += 1
                print(f"      ❌ Failed to generate embedding: {e}")
        
        # Save results
        filename = f"contentstack_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Embeddings saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving embeddings: {e}")
        
        # Show final stats
        stats = results["stats"]
        print(f"\n📈 PROCESSING COMPLETE!")
        print(f"   Total Products: {stats['total_products']}")
        print(f"   Successful Embeddings: {stats['successful_embeddings']}")
        print(f"   Failed Embeddings: {stats['failed_embeddings']}")
        print(f"   Success Rate: {(stats['successful_embeddings']/stats['total_products']*100):.1f}%")
        
        # Test similarity search
        print(f"\n🔍 Testing product similarity search...")
        
        def search_products(query_text, top_k=3):
            print(f"\n   Query: '{query_text}'")
            
            if not results["embeddings"]:
                print("      No embeddings available for search")
                return
            
            # Generate query embedding
            query_embedding = model.encode(query_text)
            
            # Calculate similarities
            similarities = []
            for uid, product_embedding in results["embeddings"].items():
                product_embedding = np.array(product_embedding)
                
                # Cosine similarity
                similarity = np.dot(query_embedding, product_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
                )
                
                metadata = results["metadata"][uid]
                similarities.append({
                    "uid": uid,
                    "title": metadata["title"],
                    "similarity": float(similarity)
                })
            
            # Sort and get top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            top_results = similarities[:top_k]
            
            for i, result in enumerate(top_results, 1):
                print(f"      {i}. {result['title']} (similarity: {result['similarity']:.4f})")
        
        # Test queries
        test_queries = ["electronics", "wireless", "premium", "office"]
        for query in test_queries:
            search_products(query, top_k=2)
        
        print(f"\n🎉 SUCCESS! Your ContentStack products now have semantic embeddings!")
        print(f"💡 You can now use these embeddings for:")
        print(f"   - Product recommendations")
        print(f"   - Semantic search")
        print(f"   - Content similarity matching")
        print(f"   - Product categorization")
        
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        print(f"\n💡 Please check:")
        print("1. ContentStack credentials are correct")
        print("2. You have a 'product' content type")
        print("3. Your delivery token has read permissions")
        print("4. Your environment name is correct")

if __name__ == "__main__":
    main()
