#!/bin/bash
# Start the FastAPI development server

echo "🚀 Starting Agentic Content Creation API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Check if required packages are installed
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Initialize database
echo "📦 Initializing database..."
python3 -c "from database import init_db; init_db()"

# Start the server
echo "🌐 Starting API server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
