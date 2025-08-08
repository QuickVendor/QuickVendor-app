# Test configuration for FastAPI
import pytest
import os
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["SLACK_WEBHOOK_URL"] = ""  # Empty for testing
os.environ["FEEDBACK_SECRET_KEY"] = ""  # Empty for testing

@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI app"""
    from app.main import app
    return app

@pytest.fixture(scope="session") 
def client(test_app):
    """Create test client"""
    return TestClient(test_app)
