#!/usr/bin/env python3
"""
Clean and reset ChromaDB vector store.

Provides options to delete collections, clear all data, or reset specific collections.
"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from agent.config import config
from agent.vector_store import VectorStore, VectorStoreError


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def clean_vector_store(collection_name: str = None, confirm: bool = True) -> None:
    """
    Clean and reset the vector store.
    
    Args:
        collection_name: Specific collection to clean (default: current config)
        confirm: Ask for confirmation before deleting
    """
    print_section("ChromaDB Vector Store Cleaner")
    
    try:
        # Initialize vector store
        print("\n📂 Initializing vector store...")
        vs = VectorStore(collection_name=collection_name)
        print(f"   ✓ Vector store initialized")
        print(f"   ✓ Persist directory: {config.vector_db_dir}")
        
    except VectorStoreError as e:
        print(f"   ✗ Error initializing vector store: {e}")
        return
    
    # List all collections
    try:
        print_section("Available Collections")
        collections = vs.list_collections()
        
        if not collections:
            print("   (No collections found)")
            print("\n✓ Vector store is already clean")
            return
        
        for i, col_name in enumerate(collections, 1):
            print(f"   {i}. {col_name}")
            
            # Get stats for each collection
            try:
                temp_vs = VectorStore(collection_name=col_name)
                stats = temp_vs.get_collection_stats()
                print(f"      Documents: {stats['total_documents']}")
            except Exception:
                pass
                
    except VectorStoreError as e:
        print(f"   ✗ Error listing collections: {e}")
        return
    
    # Get collection to clean
    target_collection = collection_name or config.collection_name
    
    # Check if collection exists
    if target_collection not in collections:
        print(f"\n⚠️  Collection '{target_collection}' not found")
        return
    
    # Get current stats
    try:
        stats = vs.get_collection_stats()
        print_section(f"Collection: {target_collection}")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Provider: {stats['provider']}")
        
    except VectorStoreError as e:
        print(f"   ✗ Error getting stats: {e}")
        return
    
    # Confirmation
    if confirm:
        print(f"\n⚠️  WARNING: This will delete all {stats['total_documents']} documents")
        print(f"   from collection '{target_collection}'")
        response = input("\n   Continue? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ Operation cancelled")
            return
    
    # Reset collection
    try:
        print(f"\n🗑️  Resetting collection '{target_collection}'...")
        vs.reset_collection()
        print("   ✓ Collection reset successfully")
        
        # Verify
        new_stats = vs.get_collection_stats()
        print(f"   ✓ Current document count: {new_stats['total_documents']}")
        
    except VectorStoreError as e:
        print(f"   ✗ Error resetting collection: {e}")
        return
    
    print_section("Clean Complete")
    print(f"✓ Collection '{target_collection}' has been reset")
    print(f"  • Documents before: {stats['total_documents']}")
    print(f"  • Documents after: {new_stats['total_documents']}")
    print()


def clean_all_collections(confirm: bool = True) -> None:
    """Clean all collections in the vector store."""
    print_section("Clean All Collections")
    
    try:
        vs = VectorStore()
        collections = vs.list_collections()
        
        if not collections:
            print("\n   (No collections found)")
            print("✓ Vector store is already clean")
            return
        
        print(f"\n   Found {len(collections)} collection(s):")
        total_docs = 0
        
        for col_name in collections:
            try:
                temp_vs = VectorStore(collection_name=col_name)
                stats = temp_vs.get_collection_stats()
                doc_count = stats['total_documents']
                total_docs += doc_count
                print(f"   • {col_name}: {doc_count} documents")
            except Exception:
                print(f"   • {col_name}: (unable to get stats)")
        
        if confirm:
            print(f"\n⚠️  WARNING: This will delete ALL {total_docs} documents")
            print(f"   from ALL {len(collections)} collection(s)")
            response = input("\n   Continue? (yes/no): ").strip().lower()
            
            if response not in ['yes', 'y']:
                print("\n❌ Operation cancelled")
                return
        
        # Delete each collection
        print(f"\n🗑️  Deleting collections...")
        for col_name in collections:
            try:
                temp_vs = VectorStore(collection_name=col_name)
                temp_vs.reset_collection()
                print(f"   ✓ Reset: {col_name}")
            except Exception as e:
                print(f"   ✗ Failed to reset {col_name}: {e}")
        
        print_section("Clean Complete")
        print(f"✓ All collections have been reset")
        print()
        
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean and reset ChromaDB vector store"
    )
    parser.add_argument(
        '--collection',
        type=str,
        help='Specific collection to clean (default: from config)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean all collections'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    if args.all:
        clean_all_collections(confirm=not args.yes)
    else:
        clean_vector_store(
            collection_name=args.collection,
            confirm=not args.yes
        )
