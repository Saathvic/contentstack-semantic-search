import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import requests

# Contentstack API credentials and parameters
stack_api_key = "bltaec246e239ee5b66"
delivery_token = "cs9bc546f25d43cfbc9312632d"
environment = "development"
content_type = "product"  # Your actual content type UID

url = f"https://eu-cdn.contentstack.com/v3/content_types/{content_type}/entries?environment={environment}"
headers = {
    "api_key": stack_api_key,
    "access_token": delivery_token,
    "Content-Type": "application/json"
}

# Initialize sentence-transformers model for embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create Pinecone client instance
pc = Pinecone(api_key="pcsk_4TbUQD_FiRGhVg9se9H9o1PWdHnfFuQz2UjQ9MdMKyTeuK9QpUeSEcjdNFmjedQ87aayWe")

# Connect to existing index
index_name = "contentstack-products"
index = pc.Index(index_name)

def fetch_and_embed_entries():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        entries = data.get("entries", [])
        print(f"Fetched {len(entries)} entries from Contentstack.")
        for i, entry in enumerate(entries, start=1):
            print(f"\nEntry {i} raw data:")
            print(entry)
            title = entry.get("title", "")
            description = entry.get("description", "")
            print("Extracted fields:")
            print(f"Title: {title}")
            print(f"Description: {description}")
            combined_text = f"{title} {description}"
            print(f"Combined text for embedding: {combined_text}")
            embedding = model.encode(combined_text)
            print(f"Embedding vector (first 5 values): {embedding[:5]}")
            entry_uid = entry.get("uid")
            # Upsert the vector with entry_uid as ID
            index.upsert([(entry_uid, embedding.tolist())])
            print(f"Upserted embedding for entry {entry_uid}")
    else:
        print(f"Failed to fetch entries: {response.status_code} {response.text}")

if __name__ == "__main__":
    fetch_and_embed_entries()
