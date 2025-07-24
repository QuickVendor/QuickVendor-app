# Test Directory for QuickVendor API

This directory contains testing resources for the QuickVendor API.

## Files

### 1. `api_test_guide.md`
A comprehensive guide for manually testing the API endpoints using Postman. This includes:
- Detailed endpoint documentation
- Request/response examples
- Environment setup instructions
- Common troubleshooting tips

### 2. `QuickVendor_API.postman_collection.json`
A ready-to-import Postman collection containing:
- Pre-configured API requests
- Environment variables
- Automated token management scripts
- Request validation tests

## Quick Start

1. **Import the Postman Collection:**
   - Open Postman
   - Click "Import" → Select `QuickVendor_API.postman_collection.json`
   - The collection will appear in your workspace

2. **Run the Backend Server:**
   ```bash
   cd /home/princewillelebhose/Documents/Projects/QuickVendor/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the Endpoints:**
   - Start with Health Check to verify the server is running
   - Register a new user
   - Login to get an access token
   - Test the protected endpoint (Get Current User)

## Notes

- The Postman collection includes automatic token management
- All test data uses environment variables for easy modification
- The collection is pre-configured with error handling and response validation
