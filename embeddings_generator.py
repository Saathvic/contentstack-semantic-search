from sentence_transformers import SentenceTransformer
import os

# Global model instance
_model = None

def get_embedding_model():
    """Get or create the sentence transformer model"""
    global _model
    if _model is None:
        print("Loading sentence transformer model...")
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("Model loaded successfully")
    return _model

def generate_embedding(text: str):
    """Generate embedding for a given text"""
    if not text or not text.strip():
        return None

    try:
        model = get_embedding_model()
        embedding = model.encode(text.strip())
        return embedding.tolist()  # Convert to list for JSON serialization
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def generate_product_embedding(product_data: dict) -> list:
    """Generate embedding from product data"""
    # Extract relevant text fields from Contentstack entry
    text_parts = []

    # Common fields that might contain searchable text
    fields_to_check = ['title', 'description', 'name', 'content', 'body', 'summary']

    for field in fields_to_check:
        if field in product_data and product_data[field]:
            if isinstance(product_data[field], str):
                text_parts.append(product_data[field])
            elif isinstance(product_data[field], dict) and 'value' in product_data[field]:
                text_parts.append(str(product_data[field]['value']))

    # Combine all text
    combined_text = ' '.join(text_parts)

    if not combined_text.strip():
        print("No searchable text found in product data")
        return None

    print(f"Generating embedding for text: {combined_text[:100]}...")
    return generate_embedding(combined_text)
