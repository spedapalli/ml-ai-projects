#!/usr/bin/env python3
"""
Script to cleanup or fix Qdrant collections .

"""
import sys
from pathlib import Path

# Add app/src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import settings
settings.patch_localhost()


from qdrant_client.models import Filter

from db.qdrant_connection import QdrantDatabaseConnector



def cleanup_all_records():
    client = QdrantDatabaseConnector()

    collections = [
        "cleaned_posts",
        "cleaned_articles",
        "cleaned_repositories",
        "vector_posts",
        "vector_articles",
        "vector_repositories"
    ]

    try :
        for collection_name in collections :
            client.delete_points(collection_name=collection_name,
                        points_selector=Filter(
                            must=[]
                        ))
            print(f"All records in {collection_name} deleted")
    except Exception as e:
        print(f"Error occured when processing collection : {collection_name}")
        raise





def fix_vector_dim():
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
    cleanup_all_records()
