#!/usr/bin/env python3
"""
Build ChromaDB vector store from markdown files in a data folder.

Chunks markdown content and creates embeddings for semantic search.
Only processes new or modified files based on tracking file.
"""

import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Set
import hashlib
from datetime import datetime

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from sentence_transformers import SentenceTransformer

from agent.config import config
from agent.vector_store import VectorStore, VectorStoreError
from agent.utils.parser import chunk_content, clean_markdown
from agent.models import BlogPost

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_file_hash(file_path: Path) -> str:
    """Calculate hash of file content for change detection."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash {file_path}: {e}")
        return ""


def load_processed_files(tracking_file: Path) -> Dict[str, Dict[str, Any]]:
    """Load previously processed files tracking data."""
    if not tracking_file.exists():
        return {}
    
    try:
        with open(tracking_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load tracking file: {e}")
        return {}


def save_processed_files(tracking_file: Path, processed_data: Dict[str, Dict[str, Any]]) -> None:
    """Save processed files tracking data."""
    try:
        tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(tracking_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save tracking file: {e}")


def find_markdown_files(data_dir: Path) -> List[Path]:
    """Find all markdown files in the data directory."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    md_files = list(data_dir.glob("**/*.md"))
    logger.info(f"Found {len(md_files)} markdown files in {data_dir}")
    return md_files


def filter_new_or_modified_files(
    md_files: List[Path],
    processed_files: Dict[str, Dict[str, Any]]
) -> tuple[List[Path], Set[str]]:
    """
    Filter files to only include new or modified ones.
    
    Returns:
        Tuple of (new/modified files, set of old file IDs to delete)
    """
    new_or_modified = []
    files_to_delete = set()
    current_files = set()
    
    for file_path in md_files:
        file_key = str(file_path)
        current_files.add(file_key)
        file_hash = get_file_hash(file_path)
        
        if file_key not in processed_files:
            # New file
            logger.info(f"New file: {file_path.name}")
            new_or_modified.append(file_path)
        elif processed_files[file_key].get('hash') != file_hash:
            # Modified file - mark old chunks for deletion
            logger.info(f"Modified file: {file_path.name}")
            new_or_modified.append(file_path)
            
            # Add old chunk IDs to deletion list
            old_chunk_count = processed_files[file_key].get('chunk_count', 0)
            for i in range(old_chunk_count):
                files_to_delete.add(f"{file_path.stem}_chunk_{i}")
    
    # Find deleted files
    for file_key in processed_files:
        if file_key not in current_files:
            logger.info(f"Deleted file: {Path(file_key).name}")
            # Add all chunks from deleted file to deletion list
            old_chunk_count = processed_files[file_key].get('chunk_count', 0)
            file_stem = Path(file_key).stem
            for i in range(old_chunk_count):
                files_to_delete.add(f"{file_stem}_chunk_{i}")
    
    return new_or_modified, files_to_delete


def read_markdown_file(file_path: Path) -> Dict[str, Any]:
    """Read and parse a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from filename or first heading
        title = file_path.stem.replace('_', ' ').replace('-', ' ')
        
        # Try to extract first heading as title
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        return {
            'file_path': file_path,
            'title': title,
            'content': content,
            'file_name': file_path.name
        }
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None


def chunk_and_embed_documents(
    md_files: List[Path],
    embed_model: SentenceTransformer,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> tuple[List[str], List[List[float]], List[Dict[str, Any]], List[str]]:
    """
    Chunk markdown files and generate embeddings.
    
    Returns:
        Tuple of (texts, embeddings, metadata, ids)
    """
    all_texts = []
    all_metadata = []
    all_ids = []
    
    logger.info(f"Processing {len(md_files)} files...")
    
    for idx, file_path in enumerate(md_files, 1):
        logger.info(f"[{idx}/{len(md_files)}] Processing: {file_path.name}")
        
        doc = read_markdown_file(file_path)
        if not doc:
            continue
        
        # Clean and chunk content
        clean_content = clean_markdown(doc['content'])
        chunks = chunk_content(
            clean_content,
            chunk_size=chunk_size,
            overlap=chunk_overlap
        )
        
        if not chunks:
            logger.warning(f"No chunks generated for {file_path.name}")
            continue
        
        logger.info(f"  Generated {len(chunks)} chunks")
        
        # Create metadata and IDs for each chunk
        for chunk_idx, chunk_text in enumerate(chunks):
            # Generate unique ID based on file path and chunk index
            doc_id = f"{file_path.stem}_chunk_{chunk_idx}"
            
            metadata = {
                'source_file': str(file_path),
                'file_name': doc['file_name'],
                'title': doc['title'],
                'chunk_index': chunk_idx,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk_text),
            }
            
            all_texts.append(chunk_text)
            all_metadata.append(metadata)
            all_ids.append(doc_id)
    
    # Generate embeddings in batch
    logger.info(f"Generating embeddings for {len(all_texts)} chunks...")
    embeddings = embed_model.encode(
        all_texts,
        show_progress_bar=True,
        batch_size=32
    )
    
    return all_texts, embeddings, all_metadata, all_ids


def build_vector_store(
    data_dir: str = None,
    collection_name: str = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    force_reset: bool = False
) -> Dict[str, Any]:
    """
    Build vector store from markdown files.
    
    Args:
        data_dir: Directory containing markdown files (default: datas)
        collection_name: Name for the vector store collection
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        force_reset: Reset existing collection and reprocess all files
    
    Returns:
        Dictionary with build statistics
    """
    print("=" * 60)
    print("  Building ChromaDB Vector Store (Incremental)")
    print("=" * 60)
    
    # Set data directory
    if data_dir is None:
        data_dir = Path(__file__).parent / "datas"
    else:
        data_dir = Path(data_dir)
    
    print(f"\n📂 Data directory: {data_dir}")
    
    # Tracking file location
    tracking_file = config.vector_db_dir / "processed_files.json"
    
    # Find markdown files
    try:
        all_md_files = find_markdown_files(data_dir)
        if not all_md_files:
            print("❌ No markdown files found!")
            return {"error": "No markdown files found"}
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return {"error": str(e)}
    
    # Load processed files tracking
    if force_reset:
        print("\n⚠️  Force reset enabled - processing all files")
        processed_files = {}
        md_files = all_md_files
        files_to_delete = set()
    else:
        processed_files = load_processed_files(tracking_file)
        md_files, files_to_delete = filter_new_or_modified_files(all_md_files, processed_files)
        
        print(f"\n📊 File status:")
        print(f"   Total files: {len(all_md_files)}")
        print(f"   New/Modified: {len(md_files)}")
        print(f"   Already processed: {len(all_md_files) - len(md_files)}")
        
        if not md_files and not files_to_delete:
            print("\n✅ All files already processed - nothing to do!")
            return {
                "success": True,
                "message": "No new or modified files",
                "files_processed": 0,
                "chunks_created": 0
            }
    
    # Initialize embedding model
    print(f"\n🤖 Loading embedding model: {config.embedding_model}")
    try:
        embed_model = SentenceTransformer(config.embedding_model)
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        return {"error": f"Failed to load embedding model: {e}"}
    
    # Initialize vector store
    print(f"\n💾 Initializing vector store...")
    try:
        vs = VectorStore(collection_name=collection_name)
        
        if force_reset:
            print("   ⚠️  Resetting existing collection...")
            vs.reset_collection()
        
        stats = vs.get_collection_stats()
        print(f"   Collection: {stats['collection_name']}")
        print(f"   Existing documents: {stats['total_documents']}")
        
    except VectorStoreError as e:
        print(f"❌ Failed to initialize vector store: {e}")
        return {"error": str(e)}
    
    # Delete old chunks from modified/deleted files
    if files_to_delete:
        print(f"\n🗑️  Removing {len(files_to_delete)} old chunks from modified/deleted files...")
        try:
            vs.delete_documents(list(files_to_delete))
            print("   ✓ Old chunks removed")
        except Exception as e:
            logger.warning(f"Failed to delete old chunks: {e}")
    
    # Chunk and embed documents
    if md_files:
        print(f"\n📝 Chunking and embedding documents...")
        print(f"   Chunk size: {chunk_size}")
        print(f"   Chunk overlap: {chunk_overlap}")
        
        try:
            texts, embeddings, metadata, ids = chunk_and_embed_documents(
                md_files,
                embed_model,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        except Exception as e:
            print(f"❌ Failed to process documents: {e}")
            return {"error": str(e)}
        
        if not texts:
            print("❌ No text chunks generated!")
            return {"error": "No text chunks generated"}
    else:
        texts, embeddings, metadata, ids = [], [], [], []
    
    # Store in vector database
    if texts:
        print(f"\n💾 Storing {len(texts)} chunks in vector database...")
        
        try:
            # ChromaDB batch size limit
            batch_size = 5000
            
            for i in range(0, len(texts), batch_size):
                end_idx = min(i + batch_size, len(texts))
                batch_texts = texts[i:end_idx]
                batch_embeddings = embeddings[i:end_idx]
                batch_metadata = metadata[i:end_idx]
                batch_ids = ids[i:end_idx]
                
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size
                print(f"   Batch {batch_num}/{total_batches}: chunks {i}-{end_idx-1}")
                
                vs.add_documents(
                    texts=batch_texts,
                    embeddings=batch_embeddings,
                    metadata=batch_metadata,
                    ids=batch_ids
                )
            
            print("   ✅ All chunks stored successfully")
            
        except VectorStoreError as e:
            print(f"❌ Failed to store documents: {e}")
            return {"error": str(e)}
    
    # Update tracking file
    print(f"\n📝 Updating tracking file...")
    
    # Update processed files dictionary
    for file_path in md_files:
        file_key = str(file_path)
        file_hash = get_file_hash(file_path)
        
        # Count chunks for this file
        chunk_count = sum(1 for m in metadata if m['source_file'] == str(file_path))
        
        processed_files[file_key] = {
            'hash': file_hash,
            'chunk_count': chunk_count,
            'processed_at': datetime.now().isoformat()
        }
    
    # Remove deleted files from tracking
    current_file_keys = {str(f) for f in all_md_files}
    processed_files = {k: v for k, v in processed_files.items() if k in current_file_keys}
    
    save_processed_files(tracking_file, processed_files)
    print(f"   ✓ Tracking file updated: {tracking_file}")
    
    # Final statistics
    final_stats = vs.get_collection_stats()
    
    print("\n" + "=" * 60)
    print("  Build Complete!")
    print("=" * 60)
    print(f"  📊 Files in directory: {len(all_md_files)}")
    print(f"  📝 Files processed this run: {len(md_files)}")
    print(f"  📄 New chunks created: {len(texts)}")
    print(f"  🗑️  Old chunks removed: {len(files_to_delete)}")
    print(f"  💾 Total documents in store: {final_stats['total_documents']}")
    print(f"  📁 Collection: {final_stats['collection_name']}")
    print(f"  📋 Tracking: {tracking_file}")
    print("=" * 60)
    print()
    
    return {
        "success": True,
        "files_processed": len(md_files),
        "chunks_created": len(texts),
        "chunks_deleted": len(files_to_delete),
        "total_documents": final_stats['total_documents'],
        "collection_name": final_stats['collection_name'],
        "tracking_file": str(tracking_file)
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build ChromaDB vector store from markdown files"
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Directory containing markdown files (default: datas)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        help='Collection name for vector store'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='Size of text chunks (default: 500)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='Overlap between chunks (default: 50)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset existing collection before building'
    )
    
    args = parser.parse_args()
    
    result = build_vector_store(
        data_dir=args.data_dir,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        force_reset=args.reset
    )
    
    # Exit with error code if build failed
    if "error" in result:
        sys.exit(1)
