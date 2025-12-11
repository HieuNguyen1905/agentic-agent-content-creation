"""
Agentic Content Creation API
============================

FastAPI server for AI-powered blog generation and management.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Initialize Database
```bash
python3 init_db.py
```

### Start Development Server
```bash
chmod +x start_api.sh
./start_api.sh
```

Or manually:
```bash
uvicorn api.main:app --reload --port 8000
```

## API Endpoints

### Health Check
- `GET /health` - Server health status
- `GET /` - API information

### Posts Management
- `GET /api/posts` - List all posts (pagination supported)
- `GET /api/posts/{slug}` - Get specific post
- `PUT /api/posts/{slug}` - Update post
- `DELETE /api/posts/{slug}` - Delete post
- `GET /api/posts/stats/overview` - Get statistics

### Content Generation
- `POST /api/generate` - Start new generation job
- `GET /api/generate/status/{job_id}` - Check job status
- `GET /api/generate/jobs` - List all jobs
- `DELETE /api/generate/jobs/{job_id}` - Delete job
- `WS /api/generate/ws/{job_id}` - Real-time updates

### Search
- `GET /api/search?q=query` - Search posts
- `GET /api/search/similar/{slug}` - Find similar posts
- `GET /api/search/suggestions?query=text` - Get suggestions
- `POST /api/search/reindex` - Rebuild search index

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/api/generate/ws/job-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Status:', data.status);
  console.log('Message:', data.message);
};

ws.send('ping'); // Keepalive
```

## Configuration

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed frontend origins
- `OPENAI_API_KEY` - OpenAI API key (if not in parent .env)

## Database Models

### BlogPost
- Stores published blog posts
- Includes SEO scores, categories, tags
- Tracks generation metadata

### GenerationJob
- Tracks async generation jobs
- Real-time status updates
- Error tracking and logs

### SearchQuery
- Analytics for search queries

### Analytics
- Basic engagement metrics

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black api/
isort api/
```

### Type Checking
```bash
mypy api/
```

## Production Deployment

### Using Docker
```bash
docker build -t agentic-api .
docker run -p 8000:8000 agentic-api
```

### Using Railway/Render
1. Connect repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Architecture

```
Frontend (Next.js) → API (FastAPI) → Agent System
                                  ↓
                              Database (SQLite/PostgreSQL)
                                  ↓
                          Vector Store (ChromaDB)
                                  ↓
                              OpenAI API
```

## Features

✅ RESTful API with FastAPI
✅ Async content generation
✅ Real-time WebSocket updates
✅ Semantic search
✅ Post management CRUD
✅ Job tracking and status
✅ Database persistence
✅ API documentation
✅ CORS support
✅ Error handling
✅ Logging

## Troubleshooting

### Port already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Database locked
```bash
rm .agent_data/blog.db
python3 init_db.py
```

### Import errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```
