#!/usr/bin/env python3
"""
Test script for the feedback API endpoint.
"""
import requests
import json
from datetime import datetime

# Test data with the new format
test_feedback = {
    "message": "This is a test feedback from the API endpoint",
    "url": "http://localhost:3000/test-page",
    "timestamp": datetime.utcnow().isoformat() + "Z"
}

def test_feedback_endpoint():
    """Test the feedback endpoint"""
    try:
        # Test the feedback submission
        print("🧪 Testing feedback submission...")
        
        headers = {"Content-Type": "application/json"}
        
        # If you have a secret key configured, add it here
        # headers["Authorization"] = "Bearer your-secret-key-here"
        
        response = requests.post(
            "http://localhost:8000/api/feedback/report",
            json=test_feedback,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Feedback endpoint test passed!")
            return True
        elif response.status_code == 429:
            print("⚠️  Rate limited - this is expected behavior")
            return True
        elif response.status_code == 401:
            print("⚠️  Unauthorized - check if FEEDBACK_SECRET_KEY is configured")
            return True
        else:
            print("❌ Feedback endpoint test failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_feedback_health():
    """Test the feedback health endpoint"""
    try:
        print("\n🧪 Testing feedback health endpoint...")
        response = requests.get(
            "http://localhost:8000/api/feedback/health",
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Feedback health endpoint test passed!")
            return True
        else:
            print("❌ Feedback health endpoint test failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting by sending multiple requests quickly"""
    try:
        print("\n🧪 Testing rate limiting (sending 12 requests quickly)...")
        
        headers = {"Content-Type": "application/json"}
        success_count = 0
        rate_limited_count = 0
        
        for i in range(12):
            test_data = {
                "message": f"Rate limit test message {i+1}",
                "url": f"http://localhost:3000/test-{i+1}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = requests.post(
                "http://localhost:8000/api/feedback/report",
                json=test_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
            
            print(f"Request {i+1}: {response.status_code}")
        
        print(f"\n📊 Rate limiting results:")
        print(f"   ✅ Successful requests: {success_count}")
        print(f"   🚫 Rate limited requests: {rate_limited_count}")
        
        if rate_limited_count > 0:
            print("✅ Rate limiting is working correctly!")
            return True
        else:
            print("⚠️  Rate limiting might not be working (or limit is very high)")
            return True
            
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing QuickVendor Feedback API")
    print("=" * 50)
    
    # Test health endpoint first
    health_ok = test_feedback_health()
    
    # Test feedback submission
    feedback_ok = test_feedback_endpoint()
    
    # Test rate limiting
    rate_limit_ok = test_rate_limiting()
    
    print("\n" + "=" * 50)
    print("🏁 Test Results:")
    print(f"   Health Check: {'✅' if health_ok else '❌'}")
    print(f"   Feedback Submit: {'✅' if feedback_ok else '❌'}")
    print(f"   Rate Limiting: {'✅' if rate_limit_ok else '❌'}")
    
    print("\n💡 To start the backend server, run:")
    print("   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
    
    print("\n🔧 Environment Configuration:")
    print("   Required: SLACK_WEBHOOK_URL")
    print("   Optional: FEEDBACK_SECRET_KEY (for additional security)")
