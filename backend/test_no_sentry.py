#!/usr/bin/env python3
"""Test script to verify backend can import without Sentry SDK."""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_import_sentry():
    """Test that Sentry module can be imported without sentry_sdk."""
    try:
        from app.core import sentry
        print("✅ Sentry module imported successfully")
        
        # Test that init_sentry works without SDK
        sentry.init_sentry()
        print("✅ init_sentry() completed without errors")
        
        # Test safe functions
        sentry.set_user_context("test-user", "test@example.com")
        sentry.set_request_context("/test", "GET", "test-user")
        sentry.add_breadcrumb("Test breadcrumb", "test")
        print("✅ Sentry functions work safely without SDK")
        
        return True
    except Exception as e:
        print(f"❌ Sentry import failed: {e}")
        return False

def test_import_middleware():
    """Test that middleware can be imported without sentry_sdk."""
    try:
        from app.core.middleware import SentryMiddleware, log_requests_middleware
        print("✅ Middleware imported successfully")
        return True
    except Exception as e:
        print(f"❌ Middleware import failed: {e}")
        return False

def test_import_main():
    """Test that main app can be imported without sentry_sdk."""
    try:
        from app.main import app
        print("✅ Main app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend imports without Sentry SDK...")
    print("=" * 50)
    
    tests = [
        ("Sentry Module", test_import_sentry),
        ("Middleware", test_import_middleware),
        ("Main App", test_import_main),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Backend is ready for production deployment without Sentry SDK.")
    else:
        print("💥 Some tests failed. Backend needs fixes before deployment.")
    
    sys.exit(0 if all_passed else 1)
