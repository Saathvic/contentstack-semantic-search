#!/usr/bin/env python3
"""
Create Pinecone index for Contentstack Semantic Search
"""

from pinecone import Pinecone, ServerlessSpec
import time

def create_pinecone_index():
    # API key from .env
    api_key = 'pcsk_4TbUQD_FiRGhVg9se9H9o1PWdHnfFuQz2UjQ9MdMKyTeuK9QpUeSEcjdNFmjedQ87aayWe'
    index_name = 'contentstack-products'

    print('🔧 Connecting to Pinecone...')
    pc = Pinecone(api_key=api_key)

    # Check if index already exists
    existing_indexes = pc.list_indexes().names()
    if index_name in existing_indexes:
        print(f'⚠️  Index "{index_name}" already exists!')
        return

    print(f'📊 Creating index "{index_name}"...')

    # Create index with correct specifications
    pc.create_index(
        name=index_name,
        dimension=384,  # sentence-transformers/all-MiniLM-L6-v2 dimension
        metric='cosine',  # Best for semantic similarity
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'  # Free tier region
        )
    )

    print('⏳ Waiting for index to be ready...')
    time.sleep(10)  # Wait for index to initialize

    # Verify index creation
    indexes = pc.list_indexes().names()
    if index_name in indexes:
        print(f'✅ Index "{index_name}" created successfully!')
        print('📋 Index Specifications:')
        print(f'   • Name: {index_name}')
        print(f'   • Dimension: 384 (sentence-transformers)')
        print(f'   • Metric: cosine similarity')
        print(f'   • Cloud: AWS us-east-1')
        print('')
        print('🎯 Ready to store and search embeddings!')
    else:
        print(f'❌ Failed to create index "{index_name}"')

if __name__ == "__main__":
    create_pinecone_index()