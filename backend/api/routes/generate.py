"""Content generation routes."""

import logging
import asyncio
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.orchestrator import BlogGenerationOrchestrator
from agent.models import GenerationSpec

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory job storage (replace with Redis in production)
generation_jobs: Dict[str, Dict[str, Any]] = {}

# WebSocket connections for real-time updates
active_connections: Dict[str, WebSocket] = {}


class GenerateRequest(BaseModel):
    """Request to generate blog content."""
    topic: str = Field(..., min_length=3, max_length=500, description="Blog post topic")
    length: str = Field("medium", pattern="^(short|medium|long)$", description="Content length")
    style: str = Field("informative", description="Writing style")
    tone: str = Field("professional", description="Writing tone")
    categories: list[str] = Field(default_factory=list, description="Post categories")
    tags: list[str] = Field(default_factory=list, description="Post tags")


class GenerateResponse(BaseModel):
    """Response from generation request."""
    job_id: str
    status: str
    message: str


class LogEntry(BaseModel):
    """Log entry for generation tracking."""
    message: str
    timestamp: str


class JobStatus(BaseModel):
    """Job status information."""
    job_id: str
    status: str
    progress: int
    topic: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: list[LogEntry] = []


async def generate_content_task(job_id: str, request: GenerateRequest):
    """Background task to generate content."""
    try:
        # Update job status
        generation_jobs[job_id]["status"] = "processing"
        generation_jobs[job_id]["progress"] = 10
        await broadcast_update(job_id, "Starting content generation...")
        
        # Create specification data
        spec_data = {
            "topic": request.topic,
            "length": request.length,
            "style": request.style,
            "tone": request.tone,
            "categories": request.categories,
            "tags": request.tags
        }
        
        generation_jobs[job_id]["progress"] = 30
        await broadcast_update(job_id, "Retrieving relevant context...")
        
        # Initialize orchestrator
        orchestrator = BlogGenerationOrchestrator()
        
        generation_jobs[job_id]["progress"] = 50
        await broadcast_update(job_id, "Composing content...")
        
        # Generate content (orchestrator expects topic and spec_data dict)
        workflow_result = await orchestrator.generate_blog_post(request.topic, spec_data)
        
        if not workflow_result.success:
            raise Exception(workflow_result.error or "Generation failed")
        
        generation_jobs[job_id]["progress"] = 100
        generation_jobs[job_id]["status"] = "completed"
        generation_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        # Extract data from WorkflowResult and final_content
        final_content = workflow_result.final_content or {}
        generation_jobs[job_id]["result"] = {
            "slug": final_content.get("slug"),
            "title": final_content.get("title"),
            "word_count": final_content.get("word_count"),
            "file_path": workflow_result.file_path,
            "seo_score": final_content.get("seo_score"),
            "iterations": workflow_result.iterations
        }
        
        await broadcast_update(job_id, f"✓ Content generated successfully: {final_content.get('title')}")
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        generation_jobs[job_id]["status"] = "failed"
        generation_jobs[job_id]["error"] = str(e)
        generation_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        await broadcast_update(job_id, f"✗ Generation failed: {str(e)}")


async def broadcast_update(job_id: str, message: str):
    """Broadcast update to connected WebSocket clients."""
    if job_id in active_connections:
        try:
            job_data = generation_jobs.get(job_id, {})
            await active_connections[job_id].send_json({
                "job_id": job_id,
                "status": job_data.get("status", "unknown"),
                "progress": job_data.get("progress", 0),
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error broadcasting to {job_id}: {e}")
    
    # Also add to logs
    if job_id in generation_jobs:
        log_entry = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        generation_jobs[job_id].setdefault("logs", []).append(log_entry)


@router.post("/", response_model=GenerateResponse)
async def generate_blog(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate a new blog post asynchronously.
    
    - **topic**: The main topic/title for the blog post
    - **length**: Content length (short: 600-1000, medium: 1000-1500, long: 1500-2500 words)
    - **style**: Writing style (informative, technical, casual, etc.)
    - **tone**: Writing tone (professional, friendly, authoritative, etc.)
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job tracking
        generation_jobs[job_id] = {
            "job_id": job_id,
            "topic": request.topic,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "logs": []
        }
        
        # Queue the generation task
        background_tasks.add_task(generate_content_task, job_id, request)
        
        logger.info(f"Created generation job {job_id} for topic: {request.topic}")
        
        return GenerateResponse(
            job_id=job_id,
            status="queued",
            message=f"Content generation started for: {request.topic}"
        )
        
    except Exception as e:
        logger.error(f"Error creating generation job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a generation job.
    
    - **job_id**: The unique job identifier
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = generation_jobs[job_id]
    return JobStatus(**job)


@router.get("/jobs")
async def list_jobs(limit: int = 20, status: Optional[str] = None):
    """
    List all generation jobs.
    
    - **limit**: Maximum number of jobs to return
    - **status**: Filter by status (queued, processing, completed, failed)
    """
    jobs = list(generation_jobs.values())
    
    # Filter by status
    if status:
        jobs = [j for j in jobs if j.get("status") == status]
    
    # Sort by created_at (newest first)
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Limit results
    return jobs[:limit]


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a generation job from tracking.
    
    - **job_id**: The job to delete
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    del generation_jobs[job_id]
    logger.info(f"Deleted job {job_id}")
    return {"message": f"Job {job_id} deleted"}


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time generation updates.
    
    - **job_id**: The job to monitor
    """
    await websocket.accept()
    active_connections[job_id] = websocket
    
    try:
        # Send current status
        if job_id in generation_jobs:
            job = generation_jobs[job_id]
            await websocket.send_json({
                "job_id": job_id,
                "status": job.get("status"),
                "progress": job.get("progress", 0),
                "message": "Connected to job stream"
            })
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "keepalive"})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
    finally:
        if job_id in active_connections:
            del active_connections[job_id]
