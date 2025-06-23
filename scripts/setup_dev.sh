#!/bin/bash
set -e

echo "🚀 Setting up Viral Content Automation Development Environment..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '3\.[0-9]+' || echo "0.0")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    echo "Please install Python 3.9 or higher and try again."
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

# Setup pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Edit .env file with your API keys"
echo "2. Start development: source venv/bin/activate"
echo "3. Run API: uvicorn src.api.main:app --reload"
echo ""
