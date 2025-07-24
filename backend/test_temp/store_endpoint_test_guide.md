# Store Endpoint Testing Guide - Task Card 5

## 📋 Overview

This guide provides testing instructions for the **Public Storefront Data** endpoint - Task Card 5.

## 🔗 Endpoint Details

### **GET /api/store/{username}**
- **Purpose**: Fetch public storefront data for customer-facing pages
- **Authentication**: **PUBLIC** (No authentication required)
- **Response**: Vendor information and available products only

---

## 🧪 Testing Instructions

### **Basic Test Setup**

#### **URL Pattern:**
```
GET http://localhost:8000/api/store/{username}
```

#### **No Authentication Required:**
- No headers needed
- No JWT token required
- Completely public endpoint

---

## 📝 Test Cases

### **Test Case 1: Valid Username (Successful)**

#### **Setup:**
1. Ensure you have a registered user with email: `testvendor@example.com`
2. Ensure this user has some products (both available and unavailable)

#### **Request:**
```
GET http://localhost:8000/api/store/testvendor
```

#### **Expected Response (200 OK):**
```json
{
  "vendor_name": "Testvendor",
  "whatsapp_number": "2348012345678",
  "products": [
    {
      "id": "product_uuid_1",
      "name": "Samsung Galaxy S24",
      "price": 999.99,
      "image_url": "/uploads/product_uuid_1.jpg"
    },
    {
      "id": "product_uuid_2", 
      "name": "Wireless Headphones",
      "price": 199.99,
      "image_url": null
    }
  ]
}
```

#### **Notes:**
- Only shows products where `is_available = true`
- `vendor_name` is extracted from email (part before @)
- All available products are included

---

### **Test Case 2: Username Not Found (Error)**

#### **Request:**
```
GET http://localhost:8000/api/store/nonexistentuser
```

#### **Expected Response (404 Not Found):**
```json
{
  "detail": "Username not found"
}
```

---

### **Test Case 3: User with No Products**

#### **Setup:**
1. Register a new user: `newvendor@example.com`
2. Don't create any products for this user

#### **Request:**
```
GET http://localhost:8000/api/store/newvendor
```

#### **Expected Response (200 OK):**
```json
{
  "vendor_name": "Newvendor",
  "whatsapp_number": "2348012345678", 
  "products": []
}
```

---

### **Test Case 4: User with Only Unavailable Products**

#### **Setup:**
1. Create products for a user
2. Set all products to `is_available = false`

#### **Expected Response (200 OK):**
```json
{
  "vendor_name": "Username",
  "whatsapp_number": "2348012345678",
  "products": []
}
```

#### **Note:**
- Products with `is_available = false` are filtered out
- Only in-stock products appear in public storefront

---

## 🔧 Testing Methods

### **Method 1: Postman**
1. **Create New Request**
   - Method: `GET`
   - URL: `http://localhost:8000/api/store/{username}`
   - Headers: None required
   - Body: None

2. **Replace {username}**
   - Use the part before @ from a registered user's email
   - Example: For `john.doe@gmail.com` use `john.doe`

### **Method 2: cURL**
```bash
# Test existing user
curl -X GET "http://localhost:8000/api/store/testvendor"

# Test non-existent user  
curl -X GET "http://localhost:8000/api/store/invaliduser"
```

### **Method 3: Browser**
```
http://localhost:8000/api/store/testvendor
```

---

## 🎯 Username Extraction Logic

The endpoint extracts usernames from email addresses:

| Email | Username to Use |
|-------|----------------|
| `john@example.com` | `john` |
| `jane.doe@gmail.com` | `jane.doe` |
| `vendor_shop@store.com` | `vendor_shop` |
| `awesome-store@business.com` | `awesome-store` |

---

## 📊 Sample Test Data

### **Create Test Scenario:**

1. **Register User:**
```json
POST /api/users/register
{
  "email": "awesomewears@example.com",
  "password": "testpass123",
  "whatsapp_number": "2348012345678"
}
```

2. **Login and Create Products:**
```
POST /api/auth/login (get token)
POST /api/products (create available product)
POST /api/products (create unavailable product)
```

3. **Test Public Storefront:**
```
GET /api/store/awesomewears
```

---

## ✅ Success Indicators

### **Valid Storefront Response Should Include:**
- ✅ `vendor_name`: Human-readable vendor name
- ✅ `whatsapp_number`: Contact number for orders
- ✅ `products`: Array of available products only
- ✅ Each product has: `id`, `name`, `price`, `image_url`

### **Filtering Works Correctly:**
- ✅ Only `is_available = true` products shown
- ✅ Unavailable products are hidden
- ✅ Empty array if no available products

### **Error Handling:**
- ✅ 404 for non-existent usernames
- ✅ Proper error message format

---

## 🌐 Frontend Integration

This endpoint is designed for:
- **Customer storefront pages**
- **Product browsing without authentication**
- **WhatsApp integration** (contact vendor directly)
- **Public product catalogs**

### **Example Frontend Usage:**
```javascript
// Fetch storefront data
const response = await fetch('/api/store/vendorname');
const storefront = await response.json();

// Display products
storefront.products.forEach(product => {
  displayProduct(product);
});

// Show WhatsApp contact
const whatsappLink = `https://wa.me/${storefront.whatsapp_number}`;
```

---

## 🔍 API Documentation

Visit the interactive documentation to test the endpoint:
- **Swagger UI**: http://localhost:8000/docs
- Look for **"storefront"** tag section
- Test directly in the browser interface

---

## 🎉 Task Card 5 Complete!

The public storefront endpoint successfully:
✅ **Fetches vendor data by username**  
✅ **Returns only available products**  
✅ **Provides public access (no authentication)**  
✅ **Handles errors appropriately**  
✅ **Formats data for customer-facing pages**  

Happy Testing! 🚀
