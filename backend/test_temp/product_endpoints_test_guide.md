# Product Endpoints Testing Guide

## 📋 Overview

This guide provides comprehensive testing instructions for all Product CRUD endpoints in the QuickVendor API.

## 🔐 Prerequisites

### 1. Server Running
Ensure the FastAPI server is running:
```bash
cd /home/princewillelebhose/Documents/Projects/QuickVendor-app/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. User Registration & Authentication
You need a valid JWT token. If you don't have one:

#### Register a new user:
```
POST http://localhost:8000/api/users/register
Content-Type: application/json

{
  "email": "testvendor@example.com",
  "password": "testpassword123",
  "whatsapp_number": "2348012345678"
}
```

#### Login to get JWT token:
```
POST http://localhost:8000/api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testvendor@example.com
password=testpassword123
```

**Copy the `access_token` from the response for use in all product endpoints.**

---

## 🛍️ Product Endpoints Testing

### 1. CREATE PRODUCT - POST /api/products

#### Basic Info:
- **URL**: `http://localhost:8000/api/products`
- **Method**: `POST`
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `multipart/form-data`
- **Expected Response**: `201 Created`

#### Postman Configuration:

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Body (form-data):**
| Key | Value | Type |
|-----|-------|------|
| name | Wireless Bluetooth Headphones | Text |
| description | Premium noise-canceling headphones with 30-hour battery life | Text |
| price | 199.99 | Text |
| is_available | true | Text |
| image | [Select your image file] | File |

#### Test Cases:

##### Test Case 1: Product with Image
```
name: Samsung Galaxy S24
description: Latest flagship smartphone with AI features and 200MP camera
price: 999.99
is_available: true
image: [Upload phone.jpg]
```

##### Test Case 2: Product without Image
```
name: Yoga Mat Premium
description: Non-slip exercise mat with alignment lines
price: 45.00
is_available: true
image: [Leave empty]
```

##### Test Case 3: Product Unavailable
```
name: Limited Edition Watch
description: Collector's timepiece with automatic movement
price: 1299.99
is_available: false
image: [Upload watch.jpg]
```

#### Expected Response:
```json
{
  "id": "product_abc123def456",
  "name": "Samsung Galaxy S24",
  "description": "Latest flagship smartphone with AI features and 200MP camera",
  "price": 999.99,
  "image_url": "/uploads/product_abc123def456.jpg",
  "is_available": true,
  "user_id": "user_xyz789",
  "created_at": "2025-07-24T19:30:00Z",
  "updated_at": null
}
```

#### cURL Example:
```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=Test Product" \
  -F "description=Test description" \
  -F "price=99.99" \
  -F "is_available=true" \
  -F "image=@/path/to/your/image.jpg"
```

---

### 2. GET ALL MY PRODUCTS - GET /api/products

#### Basic Info:
- **URL**: `http://localhost:8000/api/products`
- **Method**: `GET`
- **Authentication**: Required (Bearer Token)
- **Expected Response**: `200 OK`

#### Postman Configuration:

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Body:** None (GET request)

#### Expected Response:
```json
[
  {
    "id": "product_abc123",
    "name": "Samsung Galaxy S24",
    "description": "Latest flagship smartphone",
    "price": 999.99,
    "image_url": "/uploads/product_abc123.jpg",
    "is_available": true,
    "user_id": "user_xyz789",
    "created_at": "2025-07-24T19:30:00Z",
    "updated_at": null
  },
  {
    "id": "product_def456",
    "name": "Yoga Mat Premium",
    "description": "Non-slip exercise mat",
    "price": 45.00,
    "image_url": null,
    "is_available": true,
    "user_id": "user_xyz789",
    "created_at": "2025-07-24T19:32:00Z",
    "updated_at": null
  }
]
```

#### cURL Example:
```bash
curl -X GET "http://localhost:8000/api/products" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 3. UPDATE PRODUCT - PUT /api/products/{product_id}

#### Basic Info:
- **URL**: `http://localhost:8000/api/products/{product_id}`
- **Method**: `PUT`
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `multipart/form-data`
- **Expected Response**: `200 OK`

#### Postman Configuration:

**URL Example:**
```
http://localhost:8000/api/products/product_abc123def456
```

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Body (form-data) - All fields are optional:**
| Key | Value | Type |
|-----|-------|------|
| name | Updated Product Name | Text |
| description | Updated description text | Text |
| price | 249.99 | Text |
| is_available | false | Text |
| image | [Select new image file] | File |

#### Test Cases:

##### Test Case 1: Update Price Only
```
price: 179.99
```

##### Test Case 2: Update Name and Description
```
name: Samsung Galaxy S24 Ultra
description: Enhanced version with S Pen and larger display
```

##### Test Case 3: Update Image Only
```
image: [Upload new_image.jpg]
```

##### Test Case 4: Mark as Unavailable
```
is_available: false
```

#### Expected Response:
```json
{
  "id": "product_abc123def456",
  "name": "Updated Product Name",
  "description": "Updated description text",
  "price": 249.99,
  "image_url": "/uploads/product_abc123def456_new.jpg",
  "is_available": false,
  "user_id": "user_xyz789",
  "created_at": "2025-07-24T19:30:00Z",
  "updated_at": "2025-07-24T19:45:00Z"
}
```

#### cURL Example:
```bash
curl -X PUT "http://localhost:8000/api/products/product_abc123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=Updated Product" \
  -F "price=149.99"
```

---

### 4. DELETE PRODUCT - DELETE /api/products/{product_id}

#### Basic Info:
- **URL**: `http://localhost:8000/api/products/{product_id}`
- **Method**: `DELETE`
- **Authentication**: Required (Bearer Token)
- **Expected Response**: `204 No Content`

#### Postman Configuration:

**URL Example:**
```
http://localhost:8000/api/products/product_abc123def456
```

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**Body:** None

#### Expected Response:
- **Status Code**: `204 No Content`
- **Body**: Empty

#### cURL Example:
```bash
curl -X DELETE "http://localhost:8000/api/products/product_abc123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚨 Error Scenarios

### 1. Authentication Errors

#### 401 Unauthorized - Missing Token:
```json
{
  "detail": "Not authenticated"
}
```

#### 401 Unauthorized - Invalid Token:
```json
{
  "detail": "Could not validate credentials"
}
```

### 2. Validation Errors

#### 400 Bad Request - Invalid Price:
```json
{
  "detail": "Price must be greater than 0"
}
```

#### 422 Unprocessable Entity - Missing Required Fields:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 3. Not Found Errors

#### 404 Not Found - Product doesn't exist or not owned by user:
```json
{
  "detail": "Product not found"
}
```

---

## 📁 File Upload Guidelines

### Supported Image Formats:
- JPG/JPEG
- PNG
- GIF

### Image Upload Tips:
1. **File Size**: Keep under 10MB for optimal performance
2. **File Name**: Use descriptive names (e.g., `smartphone-front.jpg`)
3. **Resolution**: 800x600 or higher recommended
4. **Field Name**: Must be exactly `image` in form-data

### Image Storage:
- Uploaded images are stored in `/uploads/` directory
- Images are accessible via: `http://localhost:8000/uploads/filename.jpg`
- Old images are automatically deleted when updating or deleting products

---

## 🔍 Testing Checklist

### Before Testing:
- [ ] Server is running on port 8000
- [ ] You have a valid JWT token
- [ ] Token is not expired (30-minute expiry)

### Create Product:
- [ ] Test with image upload
- [ ] Test without image upload
- [ ] Test with all required fields
- [ ] Test with optional fields
- [ ] Verify image_url is populated when image is uploaded

### Get Products:
- [ ] Returns only your products
- [ ] Returns empty array for new users
- [ ] All fields are populated correctly

### Update Product:
- [ ] Test updating individual fields
- [ ] Test updating multiple fields
- [ ] Test image replacement
- [ ] Verify updated_at timestamp changes

### Delete Product:
- [ ] Returns 204 status
- [ ] Product is removed from database
- [ ] Associated image file is deleted
- [ ] Cannot access deleted product

---

## 📊 Sample Test Data

### Complete Product Data Set:
```json
[
  {
    "name": "MacBook Pro 16\"",
    "description": "Apple MacBook Pro with M3 chip, 16GB RAM, 512GB SSD",
    "price": 2499.99,
    "is_available": true
  },
  {
    "name": "Nike Running Shoes",
    "description": "Lightweight running shoes with air cushioning",
    "price": 129.99,
    "is_available": true
  },
  {
    "name": "Coffee Machine Deluxe",
    "description": "Automatic espresso machine with milk frother",
    "price": 899.99,
    "is_available": false
  },
  {
    "name": "Bluetooth Speaker",
    "description": "Waterproof portable speaker with 20-hour battery",
    "price": 79.99,
    "is_available": true
  },
  {
    "name": "Gaming Chair",
    "description": "Ergonomic gaming chair with RGB lighting",
    "price": 299.99,
    "is_available": true
  }
]
```

---

## 📞 API Documentation

### Interactive Documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Links:
- **Health Check**: http://localhost:8000/api/health
- **API Root**: http://localhost:8000/

---

## 🎯 Success Indicators

✅ **Create Product**: Returns 201 with complete product object including image_url  
✅ **Get Products**: Returns 200 with array of user's products  
✅ **Update Product**: Returns 200 with updated product object  
✅ **Delete Product**: Returns 204 with no content  
✅ **Image Upload**: image_url field contains valid file path  
✅ **Image Access**: Can view uploaded images at /uploads/filename  

Happy Testing! 🚀
