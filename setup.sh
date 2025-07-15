#!/bin/bash

# 1688.com Cost Analyzer Setup Script
# This script helps set up the environment and install dependencies

set -e  # Exit on any error

echo "🚀 Setting up 1688.com Cost Analyzer"
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if we need to install python3-venv
if ! python3 -c "import venv" 2>/dev/null; then
    echo "📦 Installing python3-venv package..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-full
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-venv
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-venv
    else
        echo "❌ Cannot install python3-venv automatically. Please install it manually."
        exit 1
    fi
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install packages
echo "📦 Installing Python packages..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ All dependencies installed successfully!"

# Check if Chrome is available
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "✅ Chrome/Chromium browser found"
else
    echo "⚠️  Chrome/Chromium browser not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y chromium-browser
    elif command -v yum &> /dev/null; then
        sudo yum install -y chromium
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y chromium
    else
        echo "❌ Cannot install Chrome automatically. Please install Chrome or Chromium browser manually."
        echo "   This is required for web scraping functionality."
    fi
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🔗 Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Test with sample data: python demo.py --sample"
echo "  3. Run the web interface: streamlit run app.py"
echo "  4. Test scraping (requires internet): python demo.py --query 'electronics' --pages 1"
echo ""
echo "📝 Usage examples:"
echo "  # Test with sample data"
echo "  python demo.py --sample --save"
echo ""
echo "  # Test scraping electronics"
echo "  python demo.py --query '电子产品' --pages 1 --save"
echo ""
echo "  # Run the web interface"
echo "  streamlit run app.py"
echo ""
echo "🌐 The web interface will be available at: http://localhost:8501"