#!/bin/bash
# Automatic dependency installation script for URL Shortener
# This script is called by Claude Code SessionStart hooks

set -e  # Exit on error

echo "=== URL Shortener: Installing Dependencies ==="

# Check if we're in Claude Code remote environment
if [ -n "$CLAUDE_CODE_REMOTE" ]; then
    echo "Running in Claude Code remote environment"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -q -r requirements.txt

echo "=== Dependencies installed successfully ==="#
echo ""
echo "Quick start:"
echo "  make dev    # Start development server"
echo "  make test   # Run tests"
echo ""
