#!/bin/bash
# Quick start script for diagram-gpt-fastapi

set -e

echo "🚀 Starting diagram-gpt-fastapi..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if Graphviz is installed
if ! command -v dot &> /dev/null; then
    echo "⚠️  WARNING: Graphviz not found!"
    echo "   Please install Graphviz:"
    echo "   - macOS: brew install graphviz"
    echo "   - Ubuntu: sudo apt-get install graphviz"
    echo ""
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "   The app will use fallback mock implementation."
    echo "   Set it with: export OPENAI_API_KEY='sk-your-key'"
    echo ""
fi

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "🎨 Web UI: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

