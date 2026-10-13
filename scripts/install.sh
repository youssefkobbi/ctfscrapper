#!/bin/bash
# Install script for ctfscrapper

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     ctfscrapper Installation Script                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "❌ Error: Python 3.8+ required (found $python_version)"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -e .

echo
echo "✅ Installation complete!"
echo
echo "Usage:"
echo "  source venv/bin/activate"
echo "  ctfscrapper -u https://ctf.example.com -U user -P pass"
echo
echo "Or run directly:"
echo "  ./venv/bin/ctfscrapper -u https://ctf.example.com -U user -P pass"
