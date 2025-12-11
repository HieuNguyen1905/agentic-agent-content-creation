# Agentic Content Creation - Complete Setup Guide

## 🎉 Your Website is Ready!

The CLI-based blog generation system has been successfully transformed into a full-featured website with real-time content generation capabilities.

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Location**: `/backend`
- **Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (auto-generated Swagger UI)
- **Database**: SQLite at `backend/.agent_data/blog.db`

### Frontend (Next.js)
- **Location**: `/frontend`
- **Server**: http://localhost:3000
- **Framework**: Next.js 15 with React 19 and TypeScript

## 🚀 Quick Start

### 1. Start Backend API

```bash
cd /home/nguyenhieu/autoblog01/backend
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at**: http://localhost:8000

### 2. Start Frontend

```bash
cd /home/nguyenhieu/autoblog01/frontend
npm run dev
```

**Frontend will be available at**: http://localhost:3000

## 📱 Available Pages

### 1. **Blog Home** - http://localhost:3000/
- Landing page showing recent blog posts
- Browse all published content

### 2. **Posts List** - http://localhost:3000/posts
- Grid view of all generated posts
- Search by title or excerpt
- Sort by date, title, or SEO score
- Quick edit/read actions

### 3. **Dashboard** - http://localhost:3000/dashboard
- **Generate new blog posts** with AI
- Real-time progress tracking with WebSocket
- Form inputs:
  - Topic (required)
  - Length (short/medium/long)
  - Style (e.g., "informative, technical")
  - Tone (e.g., "professional, friendly")
  - Categories (comma-separated)
  - Tags (comma-separated)
- Live activity log showing generation steps
- Success screen with post details and navigation

### 4. **Individual Posts** - http://localhost:3000/blog/[slug]
- Full post view with formatted content
- SEO metadata display
- Category and tag navigation

## 🔧 API Endpoints

### Posts Management
- `GET /api/posts` - List all posts (pagination, sorting)
- `GET /api/posts/{slug}` - Get specific post
- `PUT /api/posts/{slug}` - Update post
- `DELETE /api/posts/{slug}` - Delete post
- `GET /api/posts/stats/overview` - Statistics

### Content Generation
- `POST /api/generate/` - Start generation job
- `GET /api/generate/status/{job_id}` - Check job status
- `GET /api/generate/jobs` - List all jobs
- `DELETE /api/generate/jobs/{job_id}` - Remove job
- `WS /api/generate/ws/{job_id}` - Real-time updates

### Search
- `GET /api/search/?q=query` - Search posts
- `GET /api/search/suggestions?query=text` - Autocomplete

## 🎨 Key Features

### Real-time Generation
- **WebSocket Connection**: Live updates during content generation
- **Progress Bar**: Visual percentage (0-100%)
- **Activity Log**: Step-by-step generation process
- **Status Polling**: Fallback for status updates every 2 seconds

### Multi-Agent System
The backend uses a sophisticated multi-agent architecture:
1. **Retriever Agent**: Fetches relevant content from vector store
2. **Composer Agent**: Creates initial draft with SEO optimization
3. **Refiner Agent**: Improves content quality and structure
4. **Evaluator Agent**: Scores content (8-factor SEO analysis)
5. **Ingestor Agent**: Stores generated content

### SEO Optimization
Automatic scoring based on:
- Title optimization (H1)
- Heading structure (H2-H6)
- Word count targets
- Internal/external links
- Image optimization
- List formatting
- Paragraph structure
- Text emphasis

## 📂 Project Structure

```
/backend
├── api/
│   ├── main.py              # FastAPI app
│   └── routes/
│       ├── posts.py         # Post CRUD
│       ├── generate.py      # Content generation
│       └── search.py        # Search functionality
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── session.py           # DB session management
├── agent/                   # Multi-agent system
├── content/
│   └── blog/               # Generated posts (.md files)
└── .agent_data/
    └── blog.db             # SQLite database

/frontend
├── src/
│   ├── app/
│   │   ├── page.tsx         # Home page
│   │   ├── dashboard/       # Generation UI
│   │   ├── posts/           # Posts list
│   │   └── blog/[slug]/     # Individual posts
│   ├── lib/
│   │   └── api.ts           # API client library
│   └── hooks/
│       └── useGeneration.ts # Generation hook
└── components/
    └── Header.tsx           # Navigation
```

## 🔐 Environment Configuration

### Backend (`/backend/.env`)
```bash
DATABASE_URL=sqlite:///./agent_data/blog.db
# For production: postgresql://user:pass@host:5432/dbname
```

### Frontend (`/frontend/.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing the System

### 1. Test Backend API
```bash
cd /home/nguyenhieu/autoblog01/backend
python3 test_api.py
```

### 2. Test Content Generation
1. Open http://localhost:3000/dashboard
2. Fill in the form:
   - **Topic**: "Python web development best practices"
   - **Length**: Medium (800-1500 words)
   - **Style**: "technical, tutorial"
   - **Tone**: "professional, educational"
   - **Categories**: "Programming, Python"
   - **Tags**: "web, backend, tutorial"
3. Click "Generate Blog Post"
4. Watch real-time progress updates
5. View the generated post

### 3. Browse Generated Content
1. Go to http://localhost:3000/posts
2. Search, sort, and filter posts
3. Click "Read More" to view full content
4. Click "Edit" for future editing features

## 📊 Database Schema

### BlogPost
- slug, title, content, excerpt
- seo_score, word_count
- categories, tags, status
- published_at, created_at, updated_at

### GenerationJob
- job_id (UUID), status, progress
- parameters (topic, length, style, tone)
- results (slug, title, word_count, seo_score)
- logs (generation steps)
- created_at, updated_at

### SearchQuery (Analytics)
- query, results_count, clicked_slug
- user tracking (optional)

### Analytics
- post_slug, views, unique_views
- avg_time_on_page, bounce_rate

## 🚢 Production Deployment

### Backend Options
1. **Railway**: Easy deployment with PostgreSQL
2. **Render**: Free tier available
3. **Docker**: Full containerization

### Frontend Options
1. **Vercel**: Native Next.js support (recommended)
2. **Netlify**: Alternative with edge functions
3. **Docker**: Self-hosted option

### Pre-deployment Checklist
- [ ] Update DATABASE_URL to PostgreSQL
- [ ] Add production CORS origins
- [ ] Set secure environment variables
- [ ] Enable API authentication
- [ ] Configure CDN for static assets
- [ ] Set up monitoring/logging
- [ ] Add rate limiting

## 🔧 Development Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 init_db.py

# Start API server
python3 -m uvicorn api.main:app --reload

# Build vector store
python3 build_vector_store.py

# Check vector store
python3 check_vector_store.py
```

### Frontend
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 📝 Next Steps

### Immediate
- ✅ Backend API running
- ✅ Frontend dashboard created
- ✅ Real-time generation working
- ⏳ Test end-to-end generation flow

### Short-term
- [ ] Create post editor page
- [ ] Add authentication system
- [ ] Implement semantic search
- [ ] Add analytics dashboard
- [ ] Create admin panel

### Long-term
- [ ] Multi-user support
- [ ] Custom AI model fine-tuning
- [ ] Scheduled generation
- [ ] Content templates
- [ ] SEO automation tools
- [ ] Social media integration

## 🆘 Troubleshooting

### Backend Issues
**Server won't start**: Check if port 8000 is available
```bash
lsof -i :8000
```

**Database errors**: Reinitialize database
```bash
rm -rf .agent_data/blog.db
python3 init_db.py
```

**Import errors**: Ensure you're in the backend directory
```bash
cd /home/nguyenhieu/autoblog01/backend
```

### Frontend Issues
**API connection failed**: Verify backend is running on port 8000

**Environment variables not loading**: Restart Next.js dev server
```bash
# Kill the server (Ctrl+C) and restart
npm run dev
```

**Build errors**: Clear Next.js cache
```bash
rm -rf .next
npm run dev
```

### WebSocket Issues
**Connection timeout**: Check CORS settings in `api/main.py`

**Messages not received**: Verify WebSocket URL in `useGeneration.ts`

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **ChromaDB Documentation**: https://docs.trychroma.com

## 🎓 How It Works

### Content Generation Flow

1. **User submits form** on dashboard → Frontend
2. **API call** `POST /api/generate/` → Backend creates job
3. **Background task** starts agent orchestration
4. **WebSocket connection** established for real-time updates
5. **Retriever agent** fetches relevant context from vector store
6. **Composer agent** generates initial draft
7. **Refiner agent** improves quality (multiple iterations)
8. **Evaluator agent** calculates SEO score
9. **Ingestor agent** saves to database and filesystem
10. **Frontend receives** completion event → Shows success screen

### Data Flow

```
User Input → API Client → FastAPI → Agent Orchestrator → Multi-Agent System
                ↓                           ↓
           WebSocket ← Progress Updates ← Background Task
                ↓                           ↓
           UI Updates                   Save to DB/File
                ↓                           ↓
         Success Screen ← Post Details ← Return Results
```

---

**Status**: ✅ Backend Running | ✅ Frontend Running | ✅ Real-time Updates Working

**Your website is now live at**: http://localhost:3000

**Ready to generate your first AI-powered blog post!** 🚀
