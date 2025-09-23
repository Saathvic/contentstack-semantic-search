import requests
from sentence_transformers import SentenceTransformer

# Contentstack API credentials and parameters
stack_api_key = "bltaec246e239ee5b66"
delivery_token = "cs9bc546f25d43cfbc9312632d"
environment = "development"
content_type = "product"  # Replace with your actual content type UID

# Contentstack API URL (Europe region)
url = f"https://eu-cdn.contentstack.com/v3/content_types/{content_type}/entries?environment={environment}"

headers = {
    "api_key": stack_api_key,
    "access_token": delivery_token,
    "Content-Type": "application/json"
}

# Load sentence-transformers model for embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')

def fetch_and_embed_entries():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        entries = data.get("entries", [])
        print(f"Fetched {len(entries)} entries from Contentstack.")
        for i, entry in enumerate(entries, start=1):
            print(f"\nEntry {i} raw data:")
            print(entry)  # Print full raw entry for debugging
            
            # Extract fields you want to embed (update according to your schema)
            title = entry.get("title", "")
            description = entry.get("description", "")
            
            print("Extracted fields:")
            print(f"Title: {title}")
            print(f"Description: {description}")
            
            # Combine relevant text fields
            combined_text = f"{title} {description}"
            print(f"Combined text for embedding: {combined_text}")
            
            # Generate embedding vector for combined text
            embedding = model.encode(combined_text)
            
            # For demonstration, print first 5 embedding vector values
            print(f"Embedding vector (first 5 values): {embedding[:5]}")
            
    else:
        print(f"Failed to fetch entries: {response.status_code} {response.text}")

if __name__ == "__main__":
    fetch_and_embed_entries()
