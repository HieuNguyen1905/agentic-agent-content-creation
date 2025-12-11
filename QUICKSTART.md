"""
Quick Start Guide
================

## Step 1: Start the Backend API

```bash
cd /home/nguyenhieu/autoblog01/backend
./start_api.sh
```

The API will start on: http://localhost:8000

## Step 2: View API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 3: Test the API

In a new terminal:
```bash
cd /home/nguyenhieu/autoblog01/backend
python3 test_api.py
```

## Step 4: Start Frontend (Next Step)

```bash
cd /home/nguyenhieu/autoblog01/frontend
npm run dev
```

## Available Endpoints

### 📊 Posts Management
- `GET /api/posts` - List all posts
  Example: http://localhost:8000/api/posts?limit=10&offset=0

- `GET /api/posts/{slug}` - Get specific post
  Example: http://localhost:8000/api/posts/your-post-slug

- `PUT /api/posts/{slug}` - Update post
- `DELETE /api/posts/{slug}` - Delete post
- `GET /api/posts/stats/overview` - Get statistics

### 🤖 Content Generation
- `POST /api/generate/` - Generate new content
  ```bash
  curl -X POST http://localhost:8000/api/generate/ \
    -H "Content-Type: application/json" \
    -d '{
      "topic": "Your Blog Topic",
      "length": "medium",
      "style": "technical",
      "tone": "professional"
    }'
  ```

- `GET /api/generate/status/{job_id}` - Check generation status
- `GET /api/generate/jobs` - List all jobs
- `WS /api/generate/ws/{job_id}` - Real-time updates

### 🔍 Search
- `GET /api/search/?q=query` - Search posts
  Example: http://localhost:8000/api/search/?q=xiaomi&limit=5

- `GET /api/search/similar/{slug}` - Find similar posts
- `GET /api/search/suggestions?query=text` - Get suggestions

## Example: Generate Content via API

```bash
# Start generation
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in Content Creation",
    "length": "medium",
    "style": "informative",
    "tone": "professional",
    "categories": ["technology", "ai"],
    "tags": ["artificial-intelligence", "content", "automation"]
  }'

# Response:
# {
#   "job_id": "123e4567-e89b-12d3-a456-426614174000",
#   "status": "queued",
#   "message": "Content generation started for: AI in Content Creation"
# }

# Check status
curl http://localhost:8000/api/generate/status/123e4567-e89b-12d3-a456-426614174000

# When completed, the post will be saved to content/blog/
```

## WebSocket Example (Real-time Updates)

```javascript
// Connect to WebSocket
const jobId = '123e4567-e89b-12d3-a456-426614174000';
const ws = new WebSocket(`ws://localhost:8000/api/generate/ws/${jobId}`);

ws.onopen = () => {
  console.log('Connected to generation stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%`);
  console.log(`Status: ${data.status}`);
  console.log(`Message: ${data.message}`);
  
  if (data.status === 'completed') {
    console.log('Generation complete!');
    ws.close();
  }
};

// Send keepalive
setInterval(() => {
  ws.send('ping');
}, 25000);
```

## Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Dependencies missing
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database issues
```bash
rm .agent_data/blog.db
python3 init_db.py
```

### Can't import modules
```bash
export PYTHONPATH="${PYTHONPATH}:/home/nguyenhieu/autoblog01/backend"
```

## Next Steps

1. ✅ Backend API is running
2. 📝 Update frontend to use API endpoints
3. 🎨 Create dashboard UI
4. 🚀 Deploy to production

## Production Deployment

### Option 1: Railway
1. Connect GitHub repo
2. Add environment variables
3. Deploy automatically

### Option 2: Render
1. Create new Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Docker
```bash
docker build -t agentic-api .
docker run -p 8000:8000 agentic-api
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (Next.js)                │
│     http://localhost:3000                   │
└─────────────────┬───────────────────────────┘
                  │ API Calls (REST + WebSocket)
┌─────────────────▼───────────────────────────┐
│        Backend API (FastAPI)                │
│     http://localhost:8000                   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │     Agent Orchestrator              │   │
│  │  (Retriever → Composer → Refiner)   │   │
│  └─────────────────────────────────────┘   │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌───▼────┐
│SQLite │   │ChromaDB │   │OpenAI  │
│Posts  │   │Vector   │   │API     │
│Jobs   │   │Store    │   │        │
└───────┘   └─────────┘   └────────┘
```

## Features Added

✅ RESTful API with FastAPI
✅ Async job processing for content generation
✅ Real-time WebSocket updates
✅ Database persistence (SQLite)
✅ Post management (CRUD operations)
✅ Semantic search
✅ Job tracking and monitoring
✅ API documentation (Swagger/ReDoc)
✅ CORS support for frontend
✅ Error handling and logging

## What's Next?

See frontend integration guide for connecting Next.js to the API.
