#!/bin/bash

# Force Python 3.13 compatible installation with pre-compiled wheels only
echo "==> Python version check"
python --version

echo "==> Upgrading pip"
pip install --upgrade pip

echo "==> Installing core FastAPI dependencies"
pip install --only-binary=all --upgrade fastapi==0.115.6
pip install --only-binary=all --upgrade "uvicorn[standard]==0.32.1"
pip install --only-binary=all --upgrade "pydantic[email]==2.10.4"
pip install --only-binary=all --upgrade email-validator==2.1.1
pip install --only-binary=all --upgrade pydantic-settings==2.7.0
pip install --only-binary=all --upgrade python-multipart==0.0.18

echo "==> Installing authentication and security dependencies"
pip install --only-binary=all --upgrade bcrypt==4.0.1
pip install --only-binary=all --upgrade "passlib[bcrypt]==1.7.4"
pip install --only-binary=all --upgrade "python-jose[cryptography]==3.3.0"

echo "==> Installing database dependencies"
pip install --only-binary=all --upgrade sqlalchemy==2.0.36
pip install --only-binary=all --upgrade psycopg2-binary==2.9.10

echo "==> Installing HTTP client and utilities"
pip install --only-binary=all --upgrade httpx==0.24.1
pip install --only-binary=all --upgrade python-dotenv==1.0.1

echo "==> Installing Sentry SDK for production monitoring"
pip install --only-binary=all --upgrade "sentry-sdk[fastapi]==2.19.2"

echo "==> Installing AWS SDK (boto3) for S3 support - CRITICAL"
pip install boto3==1.35.0 botocore==1.35.0 s3transfer==0.10.0 jmespath==1.0.1 || {
    echo "First boto3 installation attempt failed, trying without binary constraint..."
    pip install --upgrade boto3 botocore s3transfer jmespath
}

echo "==> Installation complete - listing installed packages"
pip list

echo "==> Verifying critical imports"
python -c "import fastapi; print('FastAPI: OK')"
python -c "import uvicorn; print('Uvicorn: OK')"
python -c "import httpx; print('HTTPX: OK')"
python -c "import sqlalchemy; print('SQLAlchemy: OK')"
python -c "import psycopg2; print('PostgreSQL: OK')"
python -c "import sentry_sdk; print('Sentry: OK')"
python -c "import boto3; print(f'boto3 {boto3.__version__}: OK')" || echo "boto3: FAILED - S3 uploads will not work!"

echo "==> All dependencies installed successfully!"
