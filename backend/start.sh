#!/bin/bash

# Startup script for Render deployment

echo "🚀 Starting QuickVendor Backend..."

# Set Python path
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Create database tables if they don't exist
echo "📋 Creating database tables..."
python create_tables.py

# Create uploads directory if it doesn't exist
echo "📁 Setting up uploads directory..."
mkdir -p uploads

# Start the FastAPI application
echo "🌐 Starting FastAPI server on port ${PORT:-8000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
