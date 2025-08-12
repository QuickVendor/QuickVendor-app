# 🔴 URGENT: Fix AWS S3 Upload Issue

## Problem
Your images are not uploading to S3 because:
1. **The AWS credentials in your .env file are OLD and COMPROMISED**
2. They were exposed in Git history and likely deactivated by AWS

## Solution - Follow These Steps NOW:

### Step 1: Create NEW AWS Credentials
1. Go to AWS Console: https://console.aws.amazon.com/
2. Navigate to **IAM → Users → quickvendor-s3-admin**
3. Click **Security credentials** tab
4. Under **Access keys**, find the old key: `AKIARZDBHYH6YPS2UZXL`
5. Click **Delete** to remove it (it's compromised)
6. Click **Create access key**
7. Save the new Access Key ID and Secret Access Key

### Step 2: Update Your Local .env File
Edit `/home/princewillelebhose/Documents/Projects/QuickVendor-app/backend/.env`:

```bash
# Replace with your NEW credentials
AWS_ACCESS_KEY_ID=YOUR_NEW_ACCESS_KEY_ID_HERE
AWS_SECRET_ACCESS_KEY=YOUR_NEW_SECRET_ACCESS_KEY_HERE
AWS_REGION=eu-north-1
S3_BUCKET_NAME=quickvendor-products
```

### Step 3: Restart Your Application
```bash
# Kill the current server
pkill -f uvicorn

# Restart with new environment variables
cd /home/princewillelebhose/Documents/Projects/QuickVendor-app/backend
uvicorn app.main:app --reload --port 8000
```

### Step 4: Test S3 Upload
```bash
# Run the test script
python test_s3_connection.py
```

Expected output:
```
✅ S3 client created successfully
✅ Bucket 'quickvendor-products' exists and is accessible
✅ Successfully uploaded test file
```

### Step 5: Update Render Dashboard
1. Go to https://dashboard.render.com
2. Select your service: **quickvendor-backend**
3. Go to **Environment** tab
4. Update these variables with NEW credentials:
   - `AWS_ACCESS_KEY_ID` = [Your new access key]
   - `AWS_SECRET_ACCESS_KEY` = [Your new secret key]

## New S3 Folder Structure
Images will now be saved in:
```
quickvendor-products/
└── qv-products-img/
    └── [PRODUCT_ID]/
        └── [TIMESTAMP]_[UNIQUE_ID].[ext]
```

Example URL:
```
https://quickvendor-products.s3.eu-north-1.amazonaws.com/qv-products-img/product_123/20250811_180500_abc12345.jpg
```

## Verification
After updating credentials, when you upload a product:
1. ✅ Images will upload to S3 bucket
2. ✅ They'll be in the `qv-products-img/` folder
3. ✅ URLs will be saved to database
4. ✅ Images will be publicly accessible

## ⚠️ Security Note
**NEVER** commit AWS credentials to Git. Always use environment variables!
