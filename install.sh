#!/bin/bash

echo "========================================="
echo "Installing QuickVendor Backend Dependencies"
echo "========================================="

# Navigate to backend directory
cd backend

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements-production.txt

# Force install boto3 and dependencies
echo "Installing AWS SDK (boto3)..."
pip install boto3==1.35.0 botocore==1.35.0 s3transfer==0.10.0 jmespath==1.0.1

# Verify boto3 installation
echo "Verifying boto3 installation..."
python -c "import boto3; print(f'✅ boto3 {boto3.__version__} installed successfully')" || {
    echo "❌ boto3 installation failed! Trying alternative installation..."
    pip install --force-reinstall boto3
}

# List installed packages for debugging
echo "Checking installed packages..."
pip list | grep -E "(boto3|botocore|s3transfer)"

echo "========================================="
echo "Installation Complete"
echo "========================================="
