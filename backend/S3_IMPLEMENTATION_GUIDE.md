# S3 Implementation Guide for Quick Vendor

## Phase 2: Complete Implementation Documentation

This document provides a comprehensive guide for the S3 integration implementation in the Quick Vendor FastAPI backend.

---

## 📁 Files Created/Modified

### New Files:
1. **`app/services/s3_manager.py`** - S3 Manager service class
2. **`AWS_S3_SETUP_GUIDE.md`** - AWS IAM setup instructions
3. **`S3_IMPLEMENTATION_GUIDE.md`** - This implementation guide

### Modified Files:
1. **`requirements.txt`** - Added `boto3==1.34.34`
2. **`requirements-production.txt`** - Added `boto3==1.34.34`
3. **`app/api/products.py`** - Added S3 upload endpoints
4. **`.env.example`** - Added S3 configuration variables

---

## 🚀 New API Endpoints

### 1. Upload Product Image to S3
```http
POST /api/products/{product_id}/images/upload
```

**Request:**
- **Headers:** `Authorization: Bearer {token}`
- **Body:** `multipart/form-data`
  - `image`: File (required) - Image file to upload
  - `image_slot`: Integer (1-5) - Image slot number

**Response (200 OK):**
```json
{
  "url": "https://bucket-name.s3.region.amazonaws.com/product-images/product_id/filename.jpg",
  "key": "product-images/product_id/filename.jpg",
  "filename": "20240810_123456_abcd1234.jpg",
  "product_id": "product_12345",
  "image_slot": 1,
  "upload_timestamp": "2024-08-10T12:34:56"
}
```

### 2. Delete Product Image from S3
```http
DELETE /api/products/{product_id}/images/{image_slot}
```

**Request:**
- **Headers:** `Authorization: Bearer {token}`
- **Path Parameters:**
  - `product_id`: Product ID
  - `image_slot`: Image slot number (1-5)

**Response:** `204 No Content`

### 3. Check S3 Service Status
```http
GET /api/products/s3/status
```

**Request:**
- **Headers:** `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "status": "connected",
  "bucket_configured": true,
  "message": "S3 service is properly configured and accessible",
  "bucket_name": "quickvendor-assets",
  "region": "us-east-1"
}
```

---

## 🔧 Configuration

### Environment Variables
Add these to your `.env` file:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### Local Development
For local testing without S3, leave the AWS variables empty. The system will fall back to local file storage.

---

## 📊 S3Manager Class Features

### Core Methods:
1. **`upload_product_image()`** - Upload image to S3
2. **`delete_product_image()`** - Delete single image from S3
3. **`delete_all_product_images()`** - Delete all images for a product
4. **`validate_s3_connection()`** - Test S3 connectivity

### Features:
- **Unique filename generation** with timestamps and UUIDs
- **File validation** (format and size checks)
- **Comprehensive error handling** with specific HTTP exceptions
- **Metadata attachment** to S3 objects
- **Cache control headers** for optimal performance
- **Singleton pattern** for efficient resource usage

---

## 🧪 Testing the Implementation

### 1. Test S3 Connection
```bash
curl -X GET http://localhost:8000/api/products/s3/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Upload an Image
```bash
curl -X POST http://localhost:8000/api/products/{product_id}/images/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "image_slot=1"
```

### 3. Delete an Image
```bash
curl -X DELETE http://localhost:8000/api/products/{product_id}/images/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🛡️ Security Features

1. **Authentication Required** - All endpoints require JWT authentication
2. **Product Ownership Verification** - Users can only modify their own products
3. **File Size Limits** - Maximum 10MB per image
4. **File Type Validation** - Only image formats allowed (JPEG, PNG, GIF, WebP, BMP)
5. **IAM Least Privilege** - S3 permissions limited to specific bucket and folder
6. **Error Masking** - Sensitive error details hidden from client responses

---

## 📈 Performance Optimizations

1. **Direct Streaming** - Files streamed directly to S3 without disk storage
2. **Cache Headers** - 1-year cache control for static images
3. **Singleton S3 Client** - Reuses connection for efficiency
4. **Async Operations** - Non-blocking I/O for better performance

---

## 🐛 Error Handling

### Common Errors and Solutions:

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Invalid file format | Check file extension and MIME type |
| 401 | Not authenticated | Provide valid JWT token |
| 403 | S3 access denied | Check IAM permissions |
| 404 | Product not found | Verify product ID and ownership |
| 413 | File too large | Reduce file size to under 10MB |
| 500 | S3 not configured | Set AWS environment variables |
| 503 | S3 unavailable | Check AWS service status |

---

## 🚀 Deployment Checklist

- [ ] Set up IAM user with proper permissions (see `AWS_S3_SETUP_GUIDE.md`)
- [ ] Configure S3 bucket with `product-images/` folder
- [ ] Add AWS credentials to Render environment variables
- [ ] Install boto3 dependency (`pip install -r requirements.txt`)
- [ ] Test S3 connection using `/api/products/s3/status` endpoint
- [ ] Verify image upload functionality
- [ ] Set up CloudWatch monitoring (optional)
- [ ] Configure S3 bucket lifecycle policies for cost optimization (optional)

---

## 📝 Migration from Local Storage

If migrating existing products from local storage to S3:

1. **Identify local images**: Check `image_url_1` through `image_url_5` fields
2. **Upload to S3**: Use the new upload endpoint for each image
3. **Update database**: Replace local URLs with S3 URLs
4. **Clean up**: Delete local files after successful migration

### Migration Script Example:
```python
# Example migration logic (pseudocode)
for product in products:
    for i in range(1, 6):
        local_url = getattr(product, f'image_url_{i}')
        if local_url and not local_url.startswith('https://'):
            # Upload to S3
            s3_url = upload_to_s3(local_url, product.id, i)
            # Update database
            setattr(product, f'image_url_{i}', s3_url)
            # Delete local file
            delete_local_file(local_url)
```

---

## 🔄 Rollback Plan

If you need to disable S3 and revert to local storage:

1. Remove AWS environment variables
2. The existing `save_uploaded_file()` function will handle local uploads
3. No code changes required - the system automatically falls back

---

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

## 📞 Support

For issues or questions:
1. Check S3 status: `GET /api/products/s3/status`
2. Review CloudWatch logs in AWS Console
3. Check Sentry for error tracking
4. Review this documentation

---

*Implementation completed for Quick Vendor MVP*  
*Version: 1.0*  
*Date: August 2024*
