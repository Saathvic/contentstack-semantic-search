import requests
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")  # Get from environment variable

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def get_embedding(text):
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        embedding = response.json()
        # Average token embeddings to get a fixed-size vector
        embedding_array = np.array(embedding)
        sentence_embedding = embedding_array.mean(axis=0)
        return sentence_embedding.tolist()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    sample_text = "Comfortable and stylish red high top sneakers with white stripes."
    vector = get_embedding(sample_text)
    if vector:
        print("Generated embedding vector:")
        print(vector)
    else:
        print("Failed to generate embedding.")
