from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
import httpx
import logging
from datetime import datetime
import time
from collections import defaultdict
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting storage (in production, use Redis or similar)
rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # Max requests per window
RATE_LIMIT_WINDOW = 300   # 5 minutes in seconds

# Security
security = HTTPBearer(auto_error=False)

class FeedbackRequest(BaseModel):
    message: str
    url: str
    timestamp: str

class FeedbackResponse(BaseModel):
    success: bool
    message: str

def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting implementation."""
    current_time = time.time()
    
    # Clean old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

def verify_internal_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> bool:
    """Verify internal secret key for additional security."""
    internal_key = settings.FEEDBACK_SECRET_KEY
    
    # If no internal key is configured, skip this check
    if not internal_key:
        return True
    
    if not credentials:
        return False
    
    return credentials.credentials == internal_key

async def send_to_slack(feedback_data: FeedbackRequest) -> bool:
    """Send feedback data to Slack via webhook with comprehensive debugging."""
    slack_webhook_url = settings.SLACK_WEBHOOK_URL
    
    if not slack_webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not configured in settings")
        return False
    
    logger.info(f"🔍 SLACK WEBHOOK DEBUG - Starting send process")
    logger.info(f"🔗 Webhook URL (first 50 chars): {slack_webhook_url[:50]}...")
    logger.info(f"📝 Feedback data: URL={feedback_data.url}, Message length={len(feedback_data.message)}")
    
    try:
        # Format timestamp for display
        try:
            # Parse the ISO timestamp and format it nicely
            dt = datetime.fromisoformat(feedback_data.timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            logger.info(f"🕒 Parsed timestamp: {formatted_time}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse timestamp '{feedback_data.timestamp}': {e}")
            # If parsing fails, use the original timestamp
            formatted_time = feedback_data.timestamp
        
        # Create a simple Slack message format (recommended for webhooks)
        # Using simple text format for better compatibility
        message_text = f"""
    
📩 *New User Feedback Received*

🔗 *Page URL:* {feedback_data.url}  
🕒 *Submitted At:* {formatted_time}  

📝 *Message:*  
{feedback_data.message}
"""
        
        slack_payload = {
            "text": message_text,
            "username": "QuickVendor Feedback",
            "icon_emoji": ":speech_balloon:"
        }
        
        logger.info(f"📦 Slack payload prepared:")
        logger.info(f"   - Text length: {len(slack_payload['text'])}")
        logger.info(f"   - Full payload: {slack_payload}")
        
        # Send to Slack with explicit headers
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"🚀 Making POST request to Slack webhook...")
        logger.info(f"   - Headers: {headers}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_webhook_url,
                json=slack_payload,
                headers=headers,
                timeout=15.0  # Increased timeout
            )
            
            logger.info(f"📡 Slack webhook response received:")
            logger.info(f"   - Status Code: {response.status_code}")
            logger.info(f"   - Response Text: '{response.text}'")
            logger.info(f"   - Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                if response.text.strip() == "ok":
                    logger.info(f"✅ SUCCESS: Slack webhook accepted the message!")
                    return True
                else:
                    logger.error(f"❌ ISSUE: Slack returned 200 but unexpected response: '{response.text}'")
                    logger.error(f"   Expected: 'ok', Got: '{response.text.strip()}'")
                    return False
            else:
                logger.error(f"❌ FAILURE: Slack webhook rejected the request")
                logger.error(f"   Status: {response.status_code}")
                logger.error(f"   Response: '{response.text}'")
                logger.error(f"   This usually indicates webhook URL or payload format issues")
                return False
                
    except httpx.TimeoutException as e:
        logger.error(f"❌ TIMEOUT: Slack webhook request timed out after 15 seconds")
        logger.error(f"   Error details: {str(e)}")
        return False
    except httpx.RequestError as e:
        logger.error(f"❌ REQUEST ERROR: Network/connection issue with Slack webhook")
        logger.error(f"   Error details: {str(e)}")
        logger.error(f"   This could indicate DNS issues, network connectivity, or invalid URL")
        return False
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: Something went wrong during Slack webhook call")
        logger.error(f"   Error: {str(e)}", exc_info=True)
        return False

@router.post("/report", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest, 
    request: Request,
    authorized: bool = Depends(verify_internal_key)
):
    """
    Submit user feedback that will be forwarded to Slack.
    Includes rate limiting and optional secret key authentication.
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"📥 Feedback submission received from IP: {client_ip}")
        logger.info(f"   URL: {feedback.url}")
        logger.info(f"   Message length: {len(feedback.message)}")
        
        # Check rate limiting
        if not check_rate_limit(client_ip):
            logger.warning(f"⚠️ Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Check authorization if internal key is configured
        if not authorized:
            logger.warning(f"🚫 Unauthorized feedback attempt from IP: {client_ip}")
            raise HTTPException(
                status_code=401,
                detail="Unauthorized. Invalid or missing secret key."
            )
        
        # Validate input
        if not feedback.message.strip():
            logger.warning(f"⚠️ Empty message submitted from IP: {client_ip}")
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )
        
        if len(feedback.message.strip()) < 3:
            logger.warning(f"⚠️ Message too short from IP: {client_ip}: '{feedback.message}'")
            raise HTTPException(
                status_code=400,
                detail="Message must be at least 3 characters long."
            )
        
        # Send to Slack
        logger.info(f"🎯 Attempting to send feedback to Slack...")
        slack_success = await send_to_slack(feedback)
        
        if slack_success:
            logger.info(f"✅ Feedback successfully processed and sent to Slack")
            return FeedbackResponse(
                success=True,
                message="Thank you for your feedback! We've received it and will review it promptly."
            )
        else:
            # Even if Slack fails, we don't want to show an error to the user
            # Log it for monitoring but return success
            logger.warning("⚠️ Slack webhook failed, but returning success to user for UX")
            return FeedbackResponse(
                success=True,
                message="Thank you for your feedback! We've received it and will review it promptly."
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (rate limit, validation, auth)
        raise
    except Exception as e:
        logger.error(f"❌ Error processing feedback from {client_ip}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, we couldn't process your feedback right now. Please try again later."
        )

@router.get("/health")
async def feedback_health():
    """Health check for feedback service."""
    slack_configured = bool(settings.SLACK_WEBHOOK_URL)
    internal_key_configured = bool(settings.FEEDBACK_SECRET_KEY)
    
    logger.info(f"🏥 Health check requested")
    logger.info(f"   Slack configured: {slack_configured}")
    logger.info(f"   Internal key configured: {internal_key_configured}")
    
    return {
        "status": "OK",
        "slack_configured": slack_configured,
        "internal_key_configured": internal_key_configured,
        "rate_limit": {
            "max_requests": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        },
        "timestamp": datetime.utcnow()
    }

# Manual testing endpoint (remove in production)
@router.post("/test-slack")
async def test_slack_webhook():
    """Test the Slack webhook directly with a simple message."""
    logger.info("🧪 MANUAL TEST: Testing Slack webhook directly")
    
    test_feedback = FeedbackRequest(
        message="This is a test message from the manual test endpoint",
        url="https://test.example.com",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    result = await send_to_slack(test_feedback)
    
    return {
        "test_successful": result,
        "message": "Check the logs for detailed debugging information",
        "slack_webhook_configured": bool(settings.SLACK_WEBHOOK_URL)
    }
