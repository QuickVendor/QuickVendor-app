import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
import time

# Import the FastAPI app and feedback router
from app.main import app
from app.api.feedback import router, rate_limit_storage, RATE_LIMIT_REQUESTS

client = TestClient(app)

class TestFeedbackEndpoint:
    """Test cases for the feedback endpoint"""

    def setup_method(self):
        """Reset rate limiting before each test"""
        rate_limit_storage.clear()

    def test_feedback_health_endpoint(self):
        """Test the feedback health check endpoint"""
        response = client.get("/api/feedback/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "OK"
        assert "slack_configured" in data
        assert "internal_key_configured" in data
        assert "rate_limit" in data
        assert data["rate_limit"]["max_requests"] == RATE_LIMIT_REQUESTS
        assert "timestamp" in data

    def test_submit_valid_feedback(self):
        """Test submitting valid feedback"""
        feedback_data = {
            "message": "This is a test feedback message",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        with patch('app.api.feedback.send_to_slack', return_value=True):
            response = client.post("/api/feedback/report", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Thank you for your feedback" in data["message"]

    def test_submit_empty_message(self):
        """Test submitting feedback with empty message"""
        feedback_data = {
            "message": "",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        response = client.post("/api/feedback/report", json=feedback_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Message cannot be empty."

    def test_submit_short_message(self):
        """Test submitting feedback with message too short"""
        feedback_data = {
            "message": "Hi",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        response = client.post("/api/feedback/report", json=feedback_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Message must be at least 3 characters long."

    def test_submit_feedback_with_slack_failure(self):
        """Test that user still gets success response even if Slack fails"""
        feedback_data = {
            "message": "This is a test feedback message",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        with patch('app.api.feedback.send_to_slack', return_value=False):
            response = client.post("/api/feedback/report", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Even with Slack failure, user should get success response
        assert data["success"] is True
        assert "Thank you for your feedback" in data["message"]

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        feedback_data = {
            "message": "Rate limit test message",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        with patch('app.api.feedback.send_to_slack', return_value=True):
            # Submit feedback up to the limit
            for i in range(RATE_LIMIT_REQUESTS):
                response = client.post("/api/feedback/report", json=feedback_data)
                assert response.status_code == 200
            
            # The next request should be rate limited
            response = client.post("/api/feedback/report", json=feedback_data)
            assert response.status_code == 429
            data = response.json()
            assert data["detail"] == "Too many requests. Please try again later."

    def test_missing_required_fields(self):
        """Test submitting feedback with missing required fields"""
        # Missing message field
        feedback_data = {
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        response = client.post("/api/feedback/report", json=feedback_data)
        assert response.status_code == 422  # Validation error

        # Missing URL field
        feedback_data = {
            "message": "Test message",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        response = client.post("/api/feedback/report", json=feedback_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_json(self):
        """Test submitting invalid JSON"""
        response = client.post(
            "/api/feedback/report",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_feedback_with_auth_token_when_configured(self):
        """Test feedback submission with auth token when secret key is configured"""
        feedback_data = {
            "message": "This is a test feedback message",
            "url": "http://localhost:3000/test",
            "timestamp": "2025-08-08T12:00:00Z"
        }
        
        with patch('app.core.config.settings.FEEDBACK_SECRET_KEY', 'test-secret'):
            # Request without token should fail
            response = client.post("/api/feedback/report", json=feedback_data)
            assert response.status_code == 401
            
            # Request with wrong token should fail
            headers = {"Authorization": "Bearer wrong-token"}
            response = client.post("/api/feedback/report", json=feedback_data, headers=headers)
            assert response.status_code == 401
            
            # Request with correct token should succeed
            headers = {"Authorization": "Bearer test-secret"}
            with patch('app.api.feedback.send_to_slack', return_value=True):
                response = client.post("/api/feedback/report", json=feedback_data, headers=headers)
            assert response.status_code == 200


class TestSlackIntegration:
    """Test cases for Slack webhook integration"""

    def setup_method(self):
        """Reset any mocks before each test"""
        pass

    @pytest.mark.asyncio
    async def test_send_to_slack_success(self):
        """Test successful Slack webhook call"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        
        feedback_data = FeedbackRequest(
            message="Test feedback message",
            url="http://localhost:3000/test",
            timestamp="2025-08-08T12:00:00Z"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.headers = {}  # Fix: Add proper headers dict
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test'):
            with patch('httpx.AsyncClient.post', return_value=mock_response):
                result = await send_to_slack(feedback_data)
                assert result is True

    @pytest.mark.asyncio
    async def test_send_to_slack_failure(self):
        """Test failed Slack webhook call"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        
        feedback_data = FeedbackRequest(
            message="Test feedback message",
            url="http://localhost:3000/test",
            timestamp="2025-08-08T12:00:00Z"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test'):
            with patch('httpx.AsyncClient.post', return_value=mock_response):
                result = await send_to_slack(feedback_data)
                assert result is False

    @pytest.mark.asyncio
    async def test_send_to_slack_no_webhook_configured(self):
        """Test Slack integration when no webhook URL is configured"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        
        feedback_data = FeedbackRequest(
            message="Test feedback message",
            url="http://localhost:3000/test",
            timestamp="2025-08-08T12:00:00Z"
        )
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', None):
            result = await send_to_slack(feedback_data)
            assert result is False

    @pytest.mark.asyncio
    async def test_send_to_slack_network_error(self):
        """Test Slack integration with network error"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        import httpx
        
        feedback_data = FeedbackRequest(
            message="Test feedback message",
            url="http://localhost:3000/test",
            timestamp="2025-08-08T12:00:00Z"
        )
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test'):
            with patch('httpx.AsyncClient.post', side_effect=httpx.RequestError("Network error")):
                result = await send_to_slack(feedback_data)
                assert result is False

    @pytest.mark.asyncio
    async def test_send_to_slack_timeout(self):
        """Test Slack integration with timeout"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        import httpx
        
        feedback_data = FeedbackRequest(
            message="Test feedback message",
            url="http://localhost:3000/test",
            timestamp="2025-08-08T12:00:00Z"
        )
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test'):
            with patch('httpx.AsyncClient.post', side_effect=httpx.TimeoutException("Request timeout")):
                result = await send_to_slack(feedback_data)
                assert result is False

    @pytest.mark.asyncio
    async def test_send_to_slack_message_formatting(self):
        """Test that Slack messages are properly formatted"""
        from app.api.feedback import send_to_slack, FeedbackRequest
        
        feedback_data = FeedbackRequest(
            message="Test feedback with special characters: @#$%",
            url="http://localhost:3000/dashboard?tab=products",
            timestamp="2025-08-08T14:30:45Z"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.headers = {'content-type': 'text/plain'}  # Fix: Add proper headers dict
        
        with patch('app.core.config.settings.SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test'):
            with patch('httpx.AsyncClient.post', return_value=mock_response) as mock_post:
                result = await send_to_slack(feedback_data)
                
                assert result is True
                # Verify the call was made
                assert mock_post.called
                call_args = mock_post.call_args
                
                # Check the JSON payload
                payload = call_args.kwargs['json']
                assert payload['username'] == "QuickVendor Feedback"
                assert payload['icon_emoji'] == ":speech_balloon:"
                assert "Test feedback with special characters: @#$%" in payload['text']
                assert "http://localhost:3000/dashboard?tab=products" in payload['text']


class TestTestSlackEndpoint:
    """Test cases for the test Slack endpoint (development only)"""

    def test_test_slack_endpoint_exists(self):
        """Test that the test Slack endpoint exists"""
        response = client.post("/api/feedback/test-slack")
        
        # Should return 200 regardless of Slack configuration for testing purposes
        assert response.status_code == 200
        data = response.json()
        
        assert "test_successful" in data
        assert "slack_webhook_configured" in data
        assert "message" in data
