"""Database models for blog posts and jobs."""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class BlogPost(Base):
    """Blog post database model."""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    
    # Metadata
    date = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # SEO and analytics
    seo_score = Column(Integer)
    word_count = Column(Integer)
    read_time = Column(Integer)  # minutes
    
    # Categorization
    categories = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    # Generation metadata
    topic = Column(String(500))
    style = Column(String(100))
    tone = Column(String(100))
    iterations = Column(Integer)
    generation_time = Column(Integer)  # seconds
    
    # Status
    status = Column(String(50), default="draft", index=True)  # draft, published, archived
    
    def __repr__(self):
        return f"<BlogPost(slug='{self.slug}', title='{self.title}')>"


class GenerationJob(Base):
    """Content generation job tracking."""
    __tablename__ = "generation_jobs"
    
    id = Column(String(36), primary_key=True)  # UUID
    topic = Column(String(500), nullable=False)
    
    # Status tracking
    status = Column(String(50), default="queued", index=True)  # queued, processing, completed, failed
    progress = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Parameters
    length = Column(String(20))
    style = Column(String(100))
    tone = Column(String(100))
    categories = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    # Results
    result_slug = Column(String(255))
    word_count = Column(Integer)
    seo_score = Column(Integer)
    iterations = Column(Integer)
    
    # Error tracking
    error = Column(Text)
    
    # Logs
    logs = Column(JSON, default=list)
    
    def __repr__(self):
        return f"<GenerationJob(id='{self.id}', topic='{self.topic}', status='{self.status}')>"


class SearchQuery(Base):
    """Track search queries for analytics."""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False)
    results_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SearchQuery(query='{self.query}')>"


class Analytics(Base):
    """Basic analytics tracking."""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_slug = Column(String(255), index=True)
    
    # Metrics
    views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    avg_read_time = Column(Float)  # seconds
    
    # Engagement
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Timestamps
    last_viewed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Analytics(post='{self.post_slug}', views={self.views})>"
