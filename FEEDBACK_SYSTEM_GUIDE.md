# QuickVendor Feedback System

## Overview

The QuickVendor feedback system has been completely redesigned to replace the Sentry-based user feedback with a clean, simple solution that sends feedback directly to a Slack channel via webhook.

## Key Features

✅ **Simple User Experience**: Single textarea for feedback description  
✅ **Automatic Context**: Captures URL, timestamp, and user info automatically  
✅ **Slack Integration**: Sends beautifully formatted messages to Slack  
✅ **Floating Button**: Always accessible feedback button on all pages  
✅ **Responsive Design**: Works perfectly on desktop and mobile  
✅ **Error Handling**: Graceful fallbacks and user-friendly error messages  

## Architecture

### Frontend Components

1. **FloatingFeedbackButton** (`/frontend/src/components/FloatingFeedbackButton.tsx`)
   - Floating action button visible on all pages
   - Positioned at bottom-right with subtle animation
   - Triggers the feedback modal when clicked

2. **FeedbackModal** (`/frontend/src/components/FeedbackModal.tsx`)  
   - Simple, focused feedback form
   - Single textarea for description
   - Automatically captures URL, timestamp, user context
   - Sends data to backend API

3. **HelpModal** (`/frontend/src/components/HelpModal.tsx`)
   - Updated to use the same feedback system
   - Maintains existing help functionality
   - Removes complex Sentry integration

### Backend API

1. **Feedback Router** (`/backend/app/api/feedback.py`)
   - `POST /api/feedback/report` - Submit feedback
   - `GET /api/feedback/health` - Health check for feedback service
   - Rich Slack message formatting with user context
   - Proper error handling and logging

## Setup Instructions

### 1. Backend Configuration

Add the required environment variables:

```bash
# In backend/.env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Optional: For additional security beyond rate limiting
FEEDBACK_SECRET_KEY=your-internal-secret-key-here
```

### 2. Security Configuration

The endpoint includes multiple security layers:

**Rate Limiting (Always Active):**
- Maximum 10 requests per 5-minute window per IP address
- Automatic cleanup of old request records
- Returns HTTP 429 when limit exceeded

**Optional Secret Key Authentication:**
- Set `FEEDBACK_SECRET_KEY` environment variable to enable
- Clients must send requests with `Authorization: Bearer your-secret-key`
- Returns HTTP 401 for invalid/missing keys when configured

**Input Validation:**
- Message must be at least 3 characters long
- Returns HTTP 400 for validation errors

### 2. Slack Webhook Setup

1. Go to your Slack workspace
2. Navigate to **Settings & administration** > **Manage apps**
3. Search for "Incoming Webhooks" and install it
4. Click "Add to Slack" and select the channel for feedback
5. Copy the webhook URL and add it to your `.env` file

### 3. Backend Dependencies

The system uses `httpx` for HTTP requests. Install it:

```bash
cd backend
source .venv/bin/activate
pip install httpx==0.24.1
```

Or it will be installed automatically via `requirements.txt`.

### 4. Frontend Integration

The FloatingFeedbackButton is automatically included in the main App component and will appear on all pages.

## Usage

### For Users
1. Click the floating message icon at the bottom-right of any page
2. Describe their feedback, issue, or question in the textarea
3. Click "Submit Feedback"
4. Receive confirmation that their feedback was received

### For Developers
The feedback appears in Slack with rich formatting including:
- 📝 User's description
- 🌐 Page URL where feedback was submitted
- 🕐 Timestamp
- 👤 User information (if logged in)
- 📋 Additional context

## API Reference

### POST /api/feedback/report

Submit user feedback that will be forwarded to Slack with the exact format requested.

**Request Body:**
```json
{
  "message": "User's feedback message",
  "url": "https://yourapp.com/current/page",
  "timestamp": "2025-08-08T10:30:00.000Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Thank you for your feedback! We've received it and will review it promptly."
}
```

**Security Features:**
- **Rate Limiting**: Maximum 10 requests per 5-minute window per IP address
- **Optional Secret Key**: Set `FEEDBACK_SECRET_KEY` environment variable for additional security
- **Input Validation**: Message must be at least 3 characters long

**Slack Message Format:**
The endpoint sends messages to Slack in this exact format:
```
📩 New User Feedback
🔗 URL: [page url]
🕒 Time: [formatted timestamp]
📝 Message: [feedback text]
```

### GET /api/feedback/health

Health check for the feedback service.

**Response:**
```json
{
  "status": "OK",
  "slack_configured": true,
  "internal_key_configured": false,
  "rate_limit": {
    "max_requests": 10,
    "window_seconds": 300
  },
  "timestamp": "2025-08-08T10:30:00.000Z"
}
```

## Benefits Over Previous System

1. **Simplified UX**: No complex forms or categories - just describe the issue
2. **Better Integration**: Direct Slack integration instead of third-party service
3. **Immediate Visibility**: Feedback appears instantly in your Slack channel
4. **Lower Overhead**: No external service dependencies or additional costs
5. **Customizable**: Easy to modify message format or add features
6. **Privacy**: Feedback data stays within your infrastructure

## Customization

### Modify Slack Message Format

Edit the `send_to_slack()` function in `/backend/app/api/feedback.py` to customize the message format.

### Change Button Position

Modify the CSS classes in `/frontend/src/components/FloatingFeedbackButton.tsx` to reposition the button.

### Add More Context

Extend the `FeedbackRequest` model in `/backend/app/api/feedback.py` to capture additional context fields.

## Testing

Run the test script to verify the feedback system:

```bash
# Start the backend server
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, test the API
python test_feedback_api.py
```

## Troubleshooting

### "Failed to submit feedback"
- Check that the backend server is running
- Verify the `/api/feedback/report` endpoint is accessible
- Check browser console for network errors

### "Slack webhook failed"
- Verify `SLACK_WEBHOOK_URL` is set correctly in `.env`
- Test the webhook URL manually with curl
- Check backend logs for detailed error messages

### Feedback button not visible
- Ensure `FloatingFeedbackButton` is imported in `App.tsx`
- Check for CSS conflicts that might hide the button
- Verify the component is rendered outside any container constraints

---

🎉 **Your feedback system is now ready!** Users can easily share feedback, and you'll receive it instantly in Slack with full context.
