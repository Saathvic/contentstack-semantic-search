import requests
import os
from embeddings_generator import generate_product_embedding
from pinecone_integration import PineconeManager
from config import config
from typing import List, Dict, Any
import time

class ContentstackFetcher:
    def __init__(self):
        self.stack_api_key = config.CONTENTSTACK_STACK_API_KEY
        self.delivery_token = config.CONTENTSTACK_DELIVERY_TOKEN
        self.environment = config.CONTENTSTACK_ENVIRONMENT
        self.region = config.CONTENTSTACK_REGION
        
        if not config.validate_contentstack_config():
            raise ValueError("Contentstack API credentials not found in configuration")
        
        # Set up base URL based on region
        self.base_url = config.CONTENTSTACK_API_BASE_URL
        
        # Initialize Pinecone manager
        self.pinecone_manager = None
        try:
            self.pinecone_manager = PineconeManager()
        except Exception as e:
            print(f"Warning: Pinecone not available: {e}")

    def fetch_entries(self, content_type: str, limit: int = 100, skip: int = 0) -> Dict:
        """Fetch entries from Contentstack for a specific content type"""
        url = f"{self.base_url}/content_types/{content_type}/entries"
        
        params = {
            'environment': self.environment,
            'limit': limit,
            'skip': skip,
            'include_count': True
        }
        
        headers = {
            "api_key": self.stack_api_key,
            "access_token": self.delivery_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching entries: {e}")
            return {}

    def fetch_all_entries(self, content_type: str) -> List[Dict]:
        """Fetch all entries for a content type with pagination"""
        all_entries = []
        skip = 0
        limit = 100
        
        while True:
            print(f"Fetching entries {skip} to {skip + limit}...")
            data = self.fetch_entries(content_type, limit=limit, skip=skip)
            
            entries = data.get('entries', [])
            all_entries.extend(entries)
            
            # Check if we have all entries
            total_count = data.get('count', 0)
            if len(all_entries) >= total_count or len(entries) < limit:
                break
                
            skip += limit
            time.sleep(0.1)  # Small delay to be respectful to the API
        
        print(f"Total entries fetched: {len(all_entries)}")
        return all_entries

    def sync_entries_to_pinecone(self, content_type: str = 'product'):
        """Fetch all entries and sync them to Pinecone"""
        if not self.pinecone_manager:
            print("Pinecone not available, cannot sync")
            return
        
        print(f"Starting sync of {content_type} entries to Pinecone...")
        
        entries = self.fetch_all_entries(content_type)
        
        if not entries:
            print("No entries found to sync")
            return
        
        # Generate embeddings and prepare for Pinecone
        embeddings_dict = {}
        metadata_dict = {}
        
        for entry in entries:
            entry_uid = entry.get('uid')
            if not entry_uid:
                continue
                
            # Generate embedding
            embedding = generate_product_embedding(entry)
            if embedding:
                embeddings_dict[entry_uid] = embedding
                
                # Prepare metadata
                metadata_dict[entry_uid] = {
                    'entry_uid': entry_uid,
                    'content_type': content_type,
                    'title': entry.get('title', ''),
                    'locale': entry.get('locale', 'en-us'),
                    'url': entry.get('url', ''),
                    'publish_details': entry.get('publish_details', {})
                }
            else:
                print(f"Warning: Could not generate embedding for entry {entry_uid}")
        
        if embeddings_dict:
            print(f"Syncing {len(embeddings_dict)} embeddings to Pinecone...")
            self.pinecone_manager.upsert_embeddings(embeddings_dict, metadata_dict)
            print("Sync completed successfully!")
        else:
            print("No embeddings generated, sync aborted")

    def get_entry_details(self, content_type: str, entry_uid: str) -> Dict:
        """Fetch a specific entry by UID"""
        url = f"{self.base_url}/content_types/{content_type}/entries/{entry_uid}"
        
        params = {'environment': self.environment}
        
        headers = {
            "api_key": self.stack_api_key,
            "access_token": self.delivery_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching entry {entry_uid}: {e}")
            return {}

def main():
    """Main function for testing the Contentstack fetcher"""
    try:
        fetcher = ContentstackFetcher()
        
        # Test fetching entries
        print("Testing Contentstack API connection...")
        data = fetcher.fetch_entries('product', limit=5)
        
        if data.get('entries'):
            print(f"✅ Successfully connected! Found {len(data['entries'])} sample entries")
            
            # Ask user if they want to sync all entries
            response = input("Do you want to sync all entries to Pinecone? (y/N): ").lower().strip()
            if response == 'y':
                fetcher.sync_entries_to_pinecone('product')
        else:
            print("❌ No entries found. Check your content type and API credentials.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()