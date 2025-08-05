#!/bin/bash

# QuickVendor Deployment Verification Script
# This script tests the key endpoints to verify the network error fixes

echo "🔍 QuickVendor Deployment Verification"
echo "======================================"

# Test 1: Backend Health Check
echo ""
echo "1️⃣ Testing Backend Health..."
health_response=$(curl -s https://quickvendor-app.onrender.com/api/health)
if [[ $health_response == *"OK"* ]]; then
    echo "✅ Backend is healthy: $health_response"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Test 2: CORS Preflight Check
echo ""
echo "2️⃣ Testing CORS Configuration..."
cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS https://quickvendor-app.onrender.com/api/users/register \
    -H "Origin: https://quick-vendor-app.onrender.com" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type")

if [[ $cors_response == "200" ]]; then
    echo "✅ CORS preflight successful (HTTP $cors_response)"
else
    echo "❌ CORS preflight failed (HTTP $cors_response)"
fi

# Test 3: Login Endpoint JSON Support
echo ""
echo "3️⃣ Testing Login Endpoint JSON Support..."
login_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST https://quickvendor-app.onrender.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "nonexistent@test.com", "password": "wrongpassword"}')

http_code=$(echo "$login_response" | grep "HTTP_CODE:" | cut -d: -f2)
response_body=$(echo "$login_response" | sed '/HTTP_CODE:/d')

if [[ $http_code == "401" ]] && [[ $response_body == *"Incorrect email or password"* ]]; then
    echo "✅ Login endpoint accepts JSON (HTTP $http_code)"
    echo "   Response: $response_body"
else
    echo "❌ Login endpoint JSON support issue (HTTP $http_code)"
    echo "   Response: $response_body"
fi

# Test 4: Registration Endpoint
echo ""
echo "4️⃣ Testing Registration Endpoint..."
test_email="test$(date +%s)@example.com"
register_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST https://quickvendor-app.onrender.com/api/users/register \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$test_email\", \"password\": \"testpassword123\", \"whatsapp_number\": \"2348012345678\"}")

reg_http_code=$(echo "$register_response" | grep "HTTP_CODE:" | cut -d: -f2)
reg_response_body=$(echo "$register_response" | sed '/HTTP_CODE:/d')

if [[ $reg_http_code == "201" ]]; then
    echo "✅ Registration successful (HTTP $reg_http_code)"
    echo "   Response: $reg_response_body"
elif [[ $reg_http_code == "409" ]]; then
    echo "⚠️  Registration endpoint working - email already exists (HTTP $reg_http_code)"
else
    echo "❌ Registration failed (HTTP $reg_http_code)"
    echo "   Response: $reg_response_body"
fi

# Test 5: Frontend Accessibility
echo ""
echo "5️⃣ Testing Frontend Accessibility..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" https://quick-vendor-app.onrender.com/)
if [[ $frontend_response == "200" ]]; then
    echo "✅ Frontend is accessible (HTTP $frontend_response)"
else
    echo "❌ Frontend accessibility issue (HTTP $frontend_response)"
fi

echo ""
echo "🎯 Verification Complete!"
echo ""
echo "If all tests show ✅, the network error should be resolved."
echo "If any tests show ❌, those issues need to be addressed."
