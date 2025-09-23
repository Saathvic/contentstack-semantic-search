#!/usr/bin/env python3
"""
Verify Pinecone index setup
"""

from pinecone import Pinecone

def verify_index():
    api_key = 'pcsk_4TbUQD_FiRGhVg9se9H9o1PWdHnfFuQz2UjQ9MdMKyTeuK9QpUeSEcjdNFmjedQ87aayWe'
    pc = Pinecone(api_key=api_key)

    print('📊 Pinecone Indexes:')
    indexes = pc.list_indexes()
    for index_info in indexes:
        print(f'   • {index_info.name}: {index_info.dimension}D, {index_info.metric}')

    # Get detailed stats
    index = pc.Index('contentstack-products')
    stats = index.describe_index_stats()
    print(f'\n📈 Index Stats for "contentstack-products":')
    print(f'   • Total Vectors: {stats.total_vector_count}')
    print(f'   • Index Fullness: {stats.index_fullness:.1%}')
    print(f'   • Namespaces: {list(stats.namespaces.keys()) if stats.namespaces else "None"}')

if __name__ == "__main__":
    verify_index()