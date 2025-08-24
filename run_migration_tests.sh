#!/bin/bash

echo "🚀 Type System Migration - Installation & Test"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Install NumPy if needed
echo ""
echo "📦 Installing NumPy..."
pip3 install numpy>=1.26.0 --quiet

# Run tests
echo ""
echo "🧪 Running Type System Tests..."
cd /Users/leon/Desktop/untold_story
python3 test_type_system.py 2>&1

echo ""
echo "✅ Test run complete!"