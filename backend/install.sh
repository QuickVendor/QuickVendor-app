#!/bin/bash

# Force Python 3.13 compatible installation with pre-compiled wheels only
echo "==> Python version check"
python --version

echo "==> Upgrading pip"
pip install --upgrade pip

echo "==> Installing with only binary packages (no compilation)"
pip install --only-binary=all --upgrade fastapi==0.104.1
pip install --only-binary=all --upgrade "uvicorn[standard]==0.24.0"
pip install --only-binary=all --upgrade pydantic==2.4.2
pip install --only-binary=all --upgrade pydantic-settings==2.0.3
pip install --only-binary=all --upgrade python-multipart==0.0.6
pip install --only-binary=all --upgrade "passlib[bcrypt]==1.7.4"
pip install --only-binary=all --upgrade "python-jose[cryptography]==3.3.0"
pip install --only-binary=all --upgrade sqlalchemy==2.0.23
pip install --only-binary=all --upgrade python-dotenv==1.0.0
pip install --only-binary=all --upgrade psycopg2-binary==2.9.7

echo "==> Installation complete"
pip list
