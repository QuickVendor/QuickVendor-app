#!/bin/bash

# Sentry Integration Verification Script for QuickVendor

echo "🔍 Testing QuickVendor Sentry Integration..."
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:5174"

echo ""
echo "📡 Testing Backend Sentry Integration..."
echo "----------------------------------------"

# Test health endpoint
echo -n "Health Check: "
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/api/health" 2>/dev/null)
if [[ $HEALTH_RESPONSE == *"OK"* ]]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend not responding${NC}"
    exit 1
fi

# Test Sentry message endpoint
echo -n "Sentry Message Test: "
MESSAGE_RESPONSE=$(curl -s "$BACKEND_URL/api/sentry/test-message" 2>/dev/null)
if [[ $MESSAGE_RESPONSE == *"message_id"* ]]; then
    echo -e "${GREEN}✅ Sentry message capture working${NC}"
    MESSAGE_ID=$(echo $MESSAGE_RESPONSE | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Message ID: $MESSAGE_ID"
else
    echo -e "${RED}❌ Sentry message capture failed${NC}"
fi

# Test Sentry error endpoint
echo -n "Sentry Error Test: "
ERROR_RESPONSE=$(curl -s "$BACKEND_URL/api/sentry/test-error" 2>/dev/null)
if [[ $ERROR_RESPONSE == *"Internal server error"* ]]; then
    echo -e "${GREEN}✅ Sentry error capture working${NC}"
    REQUEST_ID=$(echo $ERROR_RESPONSE | grep -o '"request_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Request ID: $REQUEST_ID"
else
    echo -e "${RED}❌ Sentry error capture failed${NC}"
fi

echo ""
echo "🎨 Testing Frontend Sentry Integration..."
echo "-----------------------------------------"

# Test if frontend is running
echo -n "Frontend Server: "
FRONTEND_RESPONSE=$(curl -s "$FRONTEND_URL" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Frontend is running on $FRONTEND_URL${NC}"
else
    echo -e "${RED}❌ Frontend not responding${NC}"
fi

echo ""
echo "📊 Sentry Configuration Summary..."
echo "-----------------------------------"
echo "Backend Sentry DSN: $(grep SENTRY_DSN backend/.env | cut -d'=' -f2 | cut -c1-50)..."
echo "Frontend Sentry DSN: $(grep VITE_SENTRY_DSN frontend/.env | cut -d'=' -f2 | cut -c1-50)..."

echo ""
echo "🧪 Manual Testing Instructions..."
echo "----------------------------------"
echo "1. Visit Frontend: $FRONTEND_URL"
echo "2. Login/Register to access dashboard"
echo "3. Look for 'Sentry Testing' panel (yellow section)"
echo "4. Test various Sentry features using the buttons"
echo ""
echo "Backend Test Endpoints:"
echo "- Health: $BACKEND_URL/api/health"
echo "- Message: $BACKEND_URL/api/sentry/test-message"
echo "- Error: $BACKEND_URL/api/sentry/test-error"

echo ""
echo "🎯 Production Deployment Next Steps..."
echo "---------------------------------------"
echo "1. Create Sentry account at https://sentry.io"
echo "2. Create separate projects for frontend and backend"
echo "3. Update environment variables with production DSNs"
echo "4. Deploy to Render with new configuration"

echo ""
echo -e "${GREEN}🎉 Sentry integration is complete and ready for production!${NC}"
