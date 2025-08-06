#!/bin/bash

# Force Python 3.13 compatible installation with pre-compiled wheels only
echo "==> Python version check"
python --version

echo "==> Upgrading pip"
pip install --upgrade pip

echo "==> Installing with only binary packages (no compilation)"
pip install --only-binary=all --upgrade fastapi==0.115.6
pip install --only-binary=all --upgrade "uvicorn[standard]==0.32.1"
pip install --only-binary=all --upgrade "pydantic[email]==2.10.4"
pip install --only-binary=all --upgrade email-validator==2.1.1
pip install --only-binary=all --upgrade pydantic-settings==2.7.0
pip install --only-binary=all --upgrade python-multipart==0.0.18
pip install --only-binary=all --upgrade "passlib[bcrypt]==1.7.4"
pip install --only-binary=all --upgrade "python-jose[cryptography]==3.3.0"
pip install --only-binary=all --upgrade sqlalchemy==2.0.36
pip install --only-binary=all --upgrade python-dotenv==1.0.1
pip install --only-binary=all --upgrade psycopg2-binary==2.9.10

echo "==> Attempting to install Sentry SDK (optional)"
pip install --only-binary=all --upgrade "sentry-sdk[fastapi]==2.19.2" || echo "Sentry SDK installation failed - continuing without monitoring"

echo "==> Installation complete"
pip list
