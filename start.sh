#!/bin/bash

# Crypto Alert Dashboard Startup Script
echo "🚀 Starting Crypto Alert Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "env_template.txt" ]; then
        cp env_template.txt .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env with your actual API keys"
        echo "   You need at least: GNEWS_API_KEY=your_key_here"
    else
        echo "❌ env_template.txt not found"
        exit 1
    fi
fi

# Create necessary directories
mkdir -p data backups logs

echo "✅ All checks passed! Starting application..."
echo "🌐 The app will open in your browser at http://localhost:8501"
echo "📱 Press Ctrl+C to stop the application"
echo "=" * 50

# Start Streamlit
streamlit run app.py
