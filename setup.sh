#!/bin/bash
# AI Agent RAG System Startup Script for Linux/Mac

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Agent RAG System - Environment Setup                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Check if requirements are installed
pip show fastapi &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
# Check .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=sk-your-key-here"
else
    echo "✓ .env file exists"
fi

echo ""
# Create data directories
mkdir -p data/uploads
mkdir -p data/vector_store
echo "✓ Data directories ready"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Setup Complete!                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Run tests: python tests/test_all.py"
echo "3. Start server: python -m src.api.server"
echo ""
