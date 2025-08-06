#!/bin/bash

# Authentication Testing Script
# Run this in your browser console to test authentication

echo "🧪 QuickVendor Authentication Test Script"
echo "========================================="
echo ""

echo "1. Clearing existing authentication data..."
# Copy and paste this in browser console:
cat << 'EOF'
// Clear all authentication data
localStorage.clear();
console.log("✅ Cleared localStorage");

// Check for existing cookies
document.cookie.split(';').forEach(cookie => {
    if (cookie.includes('access_token')) {
        console.log("🍪 Found access_token cookie:", cookie.trim());
    }
});
EOF

echo ""
echo "2. Test login and session check..."
cat << 'EOF'
// Test session check endpoint
fetch('/api/auth/check-session', {
    credentials: 'include',
    headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('temp_debug_token')
    }
})
.then(r => r.json())
.then(data => {
    console.log("🔍 Session check result:", data);
    if (data.authenticated) {
        console.log("✅ Authentication working via:", data.source);
    } else {
        console.log("❌ Authentication failed, source:", data.source);
    }
})
.catch(err => console.error("❌ Session check failed:", err));
EOF

echo ""
echo "3. Check authentication state..."
cat << 'EOF'
// Check debug token
const debugToken = localStorage.getItem('temp_debug_token');
console.log("🔑 Debug token available:", !!debugToken);
if (debugToken) {
    console.log("🔑 Debug token (first 20 chars):", debugToken.substring(0, 20) + "...");
}

// Check cookies
const cookies = document.cookie;
console.log("🍪 All cookies:", cookies);

// Check specific access_token cookie
const accessTokenCookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('access_token='));
console.log("🍪 Access token cookie:", accessTokenCookie ? "Found" : "Not found");
EOF

echo ""
echo "Instructions:"
echo "============"
echo "1. Open your browser developer tools (F12)"
echo "2. Go to Console tab"
echo "3. Copy and paste each code block above"
echo "4. Login to your application"
echo "5. Run the test scripts again"
echo "6. Try refreshing the dashboard page"
echo ""
echo "Expected results:"
echo "- ✅ Session check should return authenticated: true"
echo "- ✅ Dashboard should not redirect on refresh"
echo "- ✅ Console should show authentication source"
echo ""
echo "Report back the console output! 🚀"
