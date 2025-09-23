import os
import json
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
import numpy as np

# Load environment variables from .env file
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

class PineconeManager:
    def __init__(self):
        # Initialize Pinecone
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not configured")

        self.pc = Pinecone(api_key=api_key)
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'contentstack-products')
        self.dimension = 384  # sentence-transformers dimension

        # Create index if it doesn't exist
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index: {self.index_name}")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"Index {self.index_name} created successfully")
            except Exception as e:
                print(f"Error creating index: {e}")
                raise
        else:
            print(f"Index {self.index_name} already exists")

        # Connect to index
        self.index = self.pc.Index(self.index_name)

    def upsert_embeddings(self, embeddings_data: Dict[str, List[float]], metadata: Dict[str, Any] = None):
        """Upsert embeddings to Pinecone"""
        vectors = []
        for product_id, embedding in embeddings_data.items():
            # Convert to list if numpy array
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            # Use individual metadata or default
            product_metadata = metadata or {'product_id': product_id}
            # Ensure product_id is always in metadata
            product_metadata['product_id'] = product_id

            vector_data = {
                'id': product_id,
                'values': embedding,
                'metadata': product_metadata
            }
            vectors.append(vector_data)

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1} with {len(batch)} vectors")
            except Exception as e:
                print(f"Error upserting batch {i//batch_size + 1}: {e}")

        print(f"Successfully upserted {len(vectors)} embeddings to Pinecone")

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> Dict:
        """Search for similar embeddings"""
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()

        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return {'matches': []}

    def delete_product(self, product_id: str):
        """Delete a product from the index"""
        try:
            self.index.delete(ids=[product_id])
            print(f"Deleted product {product_id} from Pinecone")
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")

    def get_index_stats(self):
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return None

def load_existing_embeddings(file_path: str = 'product_embeddings.json') -> Dict[str, List[float]]:
    """Load embeddings from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('embeddings', {})
    except FileNotFoundError:
        print(f"Embeddings file {file_path} not found")
        return {}
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return {}

def main():
    """Main function to initialize and populate Pinecone with existing embeddings"""
    try:
        # Initialize Pinecone manager
        pinecone_manager = PineconeManager()

        # Load existing embeddings
        embeddings = load_existing_embeddings()
        if not embeddings:
            print("No embeddings found to upload")
            return

        print(f"Loaded {len(embeddings)} embeddings")

        # Upsert embeddings to Pinecone
        pinecone_manager.upsert_embeddings(embeddings)

        # Get and display index stats
        stats = pinecone_manager.get_index_stats()
        if stats:
            print(f"Index stats: {stats}")

    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()