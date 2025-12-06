#!/usr/bin/env python3
"""
Utility script to inspect and validate ChromaDB vector store contents.

Provides detailed statistics, metadata inspection, and search testing.
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from agent.config import config
from agent.vector_store import VectorStore, VectorStoreError


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def check_vector_store() -> None:
    """Main function to check vector store status."""
    print_section("ChromaDB Vector Store Inspector")

    try:
        # Initialize vector store
        print("\n📂 Initializing vector store...")
        vs = VectorStore()
        print(f"   ✓ Vector store initialized")
        print(f"   ✓ Persist directory: {config.vector_db_dir}")
        print(f"   ✓ Collection name: {config.collection_name}")

    except VectorStoreError as e:
        print(f"   ✗ Error initializing vector store: {e}")
        return
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return

    # List available collections
    try:
        print_section("Available Collections")
        collections = vs.list_collections()
        if collections:
            for i, col_name in enumerate(collections, 1):
                print(f"   {i}. {col_name}")
        else:
            print("   (No collections found)")
    except VectorStoreError as e:
        print(f"   ✗ Error listing collections: {e}")
        return

    # Get collection statistics
    try:
        print_section("Collection Statistics")
        stats = vs.get_collection_stats()
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Collection name: {stats['collection_name']}")
        print(f"   Provider: {stats['provider']}")

        if stats['total_documents'] == 0:
            print("\n   ⚠️  Vector store is empty. Ingest documents first.")
            return

    except VectorStoreError as e:
        print(f"   ✗ Error getting statistics: {e}")
        return

    # Get sample documents
    try:
        print_section("Sample Documents (First 5)")
        if vs.collection:
            all_items = vs.collection.get(include=["documents", "metadatas", "distances"])

            if all_items and all_items["documents"]:
                for i, (doc_id, text, metadata) in enumerate(
                    zip(
                        all_items["ids"][:5],
                        all_items["documents"][:5],
                        all_items["metadatas"][:5]
                    ),
                    1
                ):
                    print(f"\n   [{i}] ID: {doc_id}")
                    print(f"       Text: {text[:100]}..." if len(text) > 100 else f"       Text: {text}")
                    print(f"       Metadata: {json.dumps(metadata, ensure_ascii=False, indent=16)}")
            else:
                print("   (No documents found)")
        else:
            print("   ✗ Collection not accessible")

    except Exception as e:
        print(f"   ✗ Error retrieving documents: {e}")

    # Test similarity search
    try:
        print_section("Test Similarity Search")
        test_query = "iphone"
        print(f"   Query: '{test_query}'")
        print(f"   Retrieving top 3 results...")

        results = vs.similarity_search(test_query, top_k=10)

        if results:
            for i, doc in enumerate(results, 1):
                relevance = doc.metadata.get("relevance_score", 0)
                print(f"\n   [{i}] Relevance: {relevance:.3f}")
                print(f"       Content: {doc.page_content[:100]}...")
                print(f"       Metadata: {doc.metadata}")
        else:
            print("   (No results found)")

    except VectorStoreError as e:
        print(f"   ✗ Search failed: {e}")
    except Exception as e:
        print(f"   ✗ Unexpected error during search: {e}")

    print_section("Summary")
    print("✓ Vector store check complete")
    print(f"  • Total documents indexed: {stats.get('total_documents', 0)}")
    print(f"  • Collection: {stats.get('collection_name', 'N/A')}")
    print(f"  • Ready for retrieval: {'Yes' if stats.get('total_documents', 0) > 0 else 'No'}")
    print()


if __name__ == "__main__":
    check_vector_store()
