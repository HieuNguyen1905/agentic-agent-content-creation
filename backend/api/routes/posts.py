"""Posts management routes."""

import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import os
import frontmatter

logger = logging.getLogger(__name__)
router = APIRouter()

# Define content directory
CONTENT_DIR = Path(__file__).parent.parent.parent / "content" / "blog"


class PostMetadata(BaseModel):
    """Blog post metadata."""
    slug: str
    title: str
    date: str
    excerpt: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
    seo_score: Optional[int] = None
    word_count: Optional[int] = None


class PostDetail(PostMetadata):
    """Detailed blog post including content."""
    content: str


class PostUpdate(BaseModel):
    """Update post request."""
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None


def parse_markdown_file(file_path: Path) -> Optional[PostDetail]:
    """Parse a markdown file with frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        slug = file_path.stem
        
        return PostDetail(
            slug=slug,
            title=post.get('title', slug),
            date=post.get('date', datetime.now().isoformat()),
            excerpt=post.get('excerpt', ''),
            categories=post.get('categories', []),
            tags=post.get('tags', []),
            seo_score=post.get('seo_score'),
            word_count=len(post.content.split()) if post.content else 0,
            content=post.content
        )
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return None


@router.get("/", response_model=List[PostMetadata])
async def list_posts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("date", pattern="^(date|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List all blog posts with pagination.
    
    - **limit**: Number of posts to return (1-100)
    - **offset**: Number of posts to skip
    - **sort**: Sort by field (date or title)
    - **order**: Sort order (asc or desc)
    """
    try:
        if not CONTENT_DIR.exists():
            return []
        
        # Get all markdown files
        md_files = list(CONTENT_DIR.glob("*.md"))
        
        # Parse posts
        posts = []
        for file_path in md_files:
            post = parse_markdown_file(file_path)
            if post:
                posts.append(PostMetadata(**post.dict()))
        
        # Sort posts
        reverse = order == "desc"
        if sort == "date":
            posts.sort(key=lambda x: x.date, reverse=reverse)
        else:
            posts.sort(key=lambda x: x.title, reverse=reverse)
        
        # Apply pagination
        total = len(posts)
        paginated = posts[offset:offset + limit]
        
        logger.info(f"Listed {len(paginated)} posts (total: {total})")
        return paginated
        
    except Exception as e:
        logger.error(f"Error listing posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{slug}", response_model=PostDetail)
async def get_post(slug: str):
    """
    Get a specific blog post by slug.
    
    - **slug**: The post slug/filename (without .md extension)
    """
    try:
        file_path = CONTENT_DIR / f"{slug}.md"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Post '{slug}' not found")
        
        post = parse_markdown_file(file_path)
        if not post:
            raise HTTPException(status_code=500, detail="Failed to parse post")
        
        logger.info(f"Retrieved post: {slug}")
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting post {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{slug}", response_model=PostDetail)
async def update_post(slug: str, update: PostUpdate):
    """
    Update an existing blog post.
    
    - **slug**: The post slug/filename
    - **update**: Fields to update
    """
    try:
        file_path = CONTENT_DIR / f"{slug}.md"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Post '{slug}' not found")
        
        # Read existing post
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Update fields
        if update.title:
            post['title'] = update.title
        if update.content:
            post.content = update.content
        if update.excerpt:
            post['excerpt'] = update.excerpt
        if update.categories:
            post['categories'] = update.categories
        if update.tags:
            post['tags'] = update.tags
        
        # Update word count and date
        post['word_count'] = len(post.content.split())
        post['updated_at'] = datetime.now().isoformat()
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        # Return updated post
        updated_post = parse_markdown_file(file_path)
        logger.info(f"Updated post: {slug}")
        return updated_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{slug}")
async def delete_post(slug: str):
    """
    Delete a blog post.
    
    - **slug**: The post slug/filename to delete
    """
    try:
        file_path = CONTENT_DIR / f"{slug}.md"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Post '{slug}' not found")
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"Deleted post: {slug}")
        return {"message": f"Post '{slug}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_stats():
    """Get overview statistics of all posts."""
    try:
        if not CONTENT_DIR.exists():
            return {
                "total_posts": 0,
                "total_words": 0,
                "avg_seo_score": 0,
                "categories": [],
                "tags": []
            }
        
        md_files = list(CONTENT_DIR.glob("*.md"))
        
        total_words = 0
        seo_scores = []
        all_categories = set()
        all_tags = set()
        
        for file_path in md_files:
            post = parse_markdown_file(file_path)
            if post:
                total_words += post.word_count or 0
                if post.seo_score:
                    seo_scores.append(post.seo_score)
                all_categories.update(post.categories)
                all_tags.update(post.tags)
        
        avg_seo = sum(seo_scores) / len(seo_scores) if seo_scores else 0
        
        return {
            "total_posts": len(md_files),
            "total_words": total_words,
            "avg_seo_score": round(avg_seo, 2),
            "avg_words_per_post": round(total_words / len(md_files)) if md_files else 0,
            "categories": sorted(list(all_categories)),
            "tags": sorted(list(all_tags))
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
