# QuickVendor API Testing Guide for Postman

## Base Configuration

### Base URL
```
http://localhost:8000
```

### Headers (Default for all requests)
- `Content-Type`: `application/json` (for JSON requests)
- `Accept`: `application/json`

## API Endpoints

### 1. Health Check (No Auth Required)

**Endpoint:** `GET /api/health`

**Postman Setup:**
- Method: `GET`
- URL: `{{base_url}}/api/health`
- Headers: None required

**Expected Response (200 OK):**
```json
{
  "status": "OK",
  "message": "QuickVendor API is healthy"
}
```

---

### 2. User Registration (No Auth Required)

**Endpoint:** `POST /api/users/register`

**Postman Setup:**
- Method: `POST`
- URL: `{{base_url}}/api/users/register`
- Headers:
  - `Content-Type`: `application/json`
- Body (raw JSON):
```json
{
  "email": "vendor@example.com",
  "password": "strongpassword123",
  "whatsapp_number": "2348012345678"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "user_29e643cc403a4f1a9f085ad3ebb7f477",
  "email": "vendor@example.com"
}
```

**Error Response (409 Conflict):**
```json
{
  "detail": "Email already registered"
}
```

**Validation Rules:**
- Email: Must be a valid email format
- Password: Minimum 8 characters
- WhatsApp Number: 10-15 digits only

---

### 3. User Login (No Auth Required)

**Endpoint:** `POST /api/auth/login`

**Postman Setup:**
- Method: `POST`
- URL: `{{base_url}}/api/auth/login`
- Headers:
  - `Content-Type`: `application/x-www-form-urlencoded`
- Body (x-www-form-urlencoded):
  - `username`: `vendor@example.com`
  - `password`: `strongpassword123`

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### 4. Get Current User Profile (Protected)

**Endpoint:** `GET /api/users/me`

**Postman Setup:**
- Method: `GET`
- URL: `{{base_url}}/api/users/me`
- Headers:
  - `Authorization`: `Bearer {{access_token}}`
  - `Accept`: `application/json`

**Expected Response (200 OK):**
```json
{
  "id": "user_29e643cc403a4f1a9f085ad3ebb7f477",
  "email": "vendor@example.com",
  "whatsapp_number": "2348012345678",
  "store_url": "yourapp.com/vendor"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

---

## Postman Environment Setup

### 1. Create Environment Variables

Create a new environment in Postman with these variables:

- `base_url`: `http://localhost:8000`
- `access_token`: _(Leave empty, will be set after login)_
- `test_email`: `testvendor@example.com`
- `test_password`: `testpassword123`
- `test_whatsapp`: `2348012345678`

### 2. Automated Token Management

In the Login request, add this to the **Tests** tab:

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
    console.log("Token saved to environment");
}
```

### 3. Pre-request Script for Protected Endpoints

For protected endpoints, you can add this pre-request script:

```javascript
if (!pm.environment.get("access_token")) {
    console.warn("No access token found. Please login first.");
}
```

---

## Testing Workflow

### Step 1: Initial Setup
1. Import this collection into Postman
2. Create the environment with variables
3. Set the active environment

### Step 2: Test Registration
1. Send the registration request
2. Verify successful response (201)
3. Try registering with the same email (should get 409 error)

### Step 3: Test Login
1. Send the login request with registered credentials
2. Verify the access token is returned
3. Check that the token is saved to environment (if using the test script)

### Step 4: Test Protected Endpoint
1. Send the GET /api/users/me request
2. Verify user profile is returned
3. Try without token (remove Authorization header) - should get 401 error

### Step 5: Token Expiry Test
1. Wait for token to expire (default: 30 minutes)
2. Try accessing protected endpoint
3. Should receive 401 error
4. Re-login to get new token

---

## Common Issues & Solutions

### Issue: "Not authenticated" error
**Solution:** Ensure the Authorization header is properly formatted: `Bearer <token>`

### Issue: "Email already registered"
**Solution:** Use a different email or clean the database

### Issue: Connection refused
**Solution:** Ensure the backend server is running on port 8000

### Issue: CORS errors (if testing from browser)
**Solution:** Use Postman instead of browser-based tools

---

## Sample Test Data

You can use these test accounts:

1. **Test Vendor 1:**
   - Email: `vendor1@test.com`
   - Password: `vendor123pass`
   - WhatsApp: `2348011111111`

2. **Test Vendor 2:**
   - Email: `vendor2@test.com`
   - Password: `vendor456pass`
   - WhatsApp: `2348022222222`

3. **Test Vendor 3:**
   - Email: `vendor3@test.com`
   - Password: `vendor789pass`
   - WhatsApp: `2348033333333`

