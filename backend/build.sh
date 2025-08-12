#!/bin/bash
# Build script for Render deployment

echo "========================================="
echo "Starting QuickVendor Backend Build"
echo "========================================="

# Install requirements
echo "Installing requirements from requirements-production.txt..."
pip install -r requirements-production.txt

# Force install boto3 (in case it's not installing from requirements)
echo "Force installing boto3..."
pip install boto3==1.40.7

# Verify boto3 installation
echo "Verifying boto3 installation..."
python -c "import boto3; print(f'✅ boto3 {boto3.__version__} installed successfully')" || echo "❌ boto3 installation failed!"

# Check environment variables
echo "Checking environment variables..."
python -c "
import os
print(f'ENVIRONMENT: {os.getenv(\"ENVIRONMENT\", \"NOT SET\")}')
print(f'AWS_ACCESS_KEY_ID: {\"SET\" if os.getenv(\"AWS_ACCESS_KEY_ID\") else \"NOT SET\"}')
print(f'AWS_SECRET_ACCESS_KEY: {\"SET\" if os.getenv(\"AWS_SECRET_ACCESS_KEY\") else \"NOT SET\"}')
print(f'S3_BUCKET_NAME: {os.getenv(\"S3_BUCKET_NAME\", \"NOT SET\")}')
"

# List installed packages
echo "Installed packages:"
pip list | grep -E "(boto3|botocore)"

echo "========================================="
echo "Build Complete"
echo "=========================================
