#!/usr/bin/env python3
"""
Script to delete and recreate Qdrant collections with correct vector dimensions.
Run this after fixing the vector dimension configuration bug.
"""
import sys
sys.path.insert(0, '/app/src')

from db.qdrant_connection import QdrantDatabaseConnector

def main():
    client = QdrantDatabaseConnector()

    # Collections to recreate
    vector_collections = [
        "vector_posts",
        "vector_articles",
        "vector_repositories"
    ]

    print("Deleting old collections with incorrect vector dimensions...")
    for collection_name in vector_collections:
        try:
            client._instance.delete_collection(collection_name=collection_name)
            print(f"✓ Deleted collection: {collection_name}")
        except Exception as e:
            print(f"  Collection {collection_name} doesn't exist or error: {e}")

    print("\nRecreating collections with correct vector dimensions...")
    for collection_name in vector_collections:
        try:
            client.create_vector_collection(collection_name=collection_name)
            info = client.get_collection(collection_name=collection_name)
            print(f"✓ Created {collection_name} with vector size: {info.config.params.vectors.size}")
        except Exception as e:
            print(f"✗ Failed to create {collection_name}: {e}")

    print("\nDone! Collections recreated with correct dimensions:")
    print("  - vector_posts: 384 dims")
    print("  - vector_articles: 384 dims")
    print("  - vector_repositories: 768 dims")

if __name__ == "__main__":
    main()
