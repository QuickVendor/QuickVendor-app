#!/bin/bash

# QuickVendor Complete Deployment Verification Script
# Tests both backend API and frontend routing functionality

echo "🔍 QuickVendor Complete Deployment Verification"
echo "=============================================="

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
    
    # Test 5: Auto-login after registration
    echo ""
    echo "5️⃣ Testing Auto-Login Flow..."
    login_test_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
        -X POST https://quickvendor-app.onrender.com/api/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$test_email\", \"password\": \"testpassword123\"}")
    
    login_test_code=$(echo "$login_test_response" | grep "HTTP_CODE:" | cut -d: -f2)
    login_test_body=$(echo "$login_test_response" | sed '/HTTP_CODE:/d')
    
    if [[ $login_test_code == "200" ]] && [[ $login_test_body == *"access_token"* ]]; then
        echo "✅ Auto-login flow working (HTTP $login_test_code)"
        echo "   Access token received successfully"
    else
        echo "❌ Auto-login flow failed (HTTP $login_test_code)"
        echo "   Response: $login_test_body"
    fi
    
elif [[ $reg_http_code == "409" ]]; then
    echo "⚠️  Registration endpoint working - email already exists (HTTP $reg_http_code)"
else
    echo "❌ Registration failed (HTTP $reg_http_code)"
    echo "   Response: $reg_response_body"
fi

# Test 6: Frontend Accessibility
echo ""
echo "6️⃣ Testing Frontend Accessibility..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" https://quick-vendor-app.onrender.com/)
if [[ $frontend_response == "200" ]]; then
    echo "✅ Frontend is accessible (HTTP $frontend_response)"
else
    echo "❌ Frontend accessibility issue (HTTP $frontend_response)"
fi

# Test 7: Frontend Routes Test
echo ""
echo "7️⃣ Testing Frontend SPA Routes..."
auth_route_response=$(curl -s -o /dev/null -w "%{http_code}" https://quick-vendor-app.onrender.com/auth)
dashboard_route_response=$(curl -s -o /dev/null -w "%{http_code}" https://quick-vendor-app.onrender.com/dashboard)

if [[ $auth_route_response == "200" ]]; then
    echo "✅ Auth route accessible (HTTP $auth_route_response)"
else
    echo "❌ Auth route issue (HTTP $auth_route_response)"
fi

if [[ $dashboard_route_response == "200" ]]; then
    echo "✅ Dashboard route accessible (HTTP $dashboard_route_response)"
else
    echo "❌ Dashboard route issue (HTTP $dashboard_route_response)"
fi

echo ""
echo "🎯 Verification Complete!"
echo ""
echo "📊 SUMMARY:"
echo "- Backend API: $([ $http_code == "401" ] && echo "✅ Working" || echo "❌ Issues")"
echo "- CORS Config: $([ $cors_response == "200" ] && echo "✅ Working" || echo "❌ Issues")" 
echo "- Registration: $([ $reg_http_code == "201" ] || [ $reg_http_code == "409" ] && echo "✅ Working" || echo "❌ Issues")"
echo "- Frontend: $([ $frontend_response == "200" ] && echo "✅ Working" || echo "❌ Issues")"
echo ""
echo "$([ $http_code == "401" ] && [ $cors_response == "200" ] && ([ $reg_http_code == "201" ] || [ $reg_http_code == "409" ]) && [ $frontend_response == "200" ] && echo "🎉 ALL SYSTEMS OPERATIONAL! Ready for production use! 🚀" || echo "⚠️  Some issues detected. Check the logs above.")"
