# 🚀 Render Deployment Checklist for S3 Integration

## ✅ Pre-Deployment Verification

### 1. AWS Credentials Setup
**⚠️ CRITICAL: Use NEW credentials (the old ones were exposed)**

- [ ] **Create new AWS IAM credentials**
  1. Go to AWS IAM Console
  2. Delete the old access key: `AKIARZDBHYH6YPS2UZXL`
  3. Create new Access Key for user `quickvendor-s3-admin`
  4. Save the new credentials securely

### 2. Configure Environment Variables in Render Dashboard

Go to your Render service dashboard → Environment → Add the following:

| Variable | Value | Notes |
|----------|-------|-------|
| `AWS_ACCESS_KEY_ID` | Your NEW Access Key ID | ⚠️ Use NEW credentials |
| `AWS_SECRET_ACCESS_KEY` | Your NEW Secret Access Key | ⚠️ Use NEW credentials |
| `AWS_REGION` | `eu-north-1` | Already in render.yaml |
| `S3_BUCKET_NAME` | `quickvendor-products` | Already in render.yaml |

**Note:** The variables marked with `sync: false` in render.yaml MUST be added manually in Render's dashboard.

### 3. Verify S3 Bucket Configuration

- [x] Bucket exists: `quickvendor-products`
- [x] Bucket region: `eu-north-1`
- [ ] **Bucket permissions** - Ensure the IAM user has these permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::quickvendor-products/*",
          "arn:aws:s3:::quickvendor-products"
        ]
      }
    ]
  }
  ```

### 4. S3 Bucket Public Access Settings

For images to be publicly accessible, configure:

1. **Bucket Policy** (add this to your S3 bucket):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::quickvendor-products/product-images/*"
    }
  ]
}
```

2. **Block Public Access Settings**:
   - Block public access to buckets and objects granted through new access control lists (ACLs): ✅ On
   - Block public access to buckets and objects granted through any access control lists (ACLs): ✅ On
   - Block public access to buckets and objects granted through new public bucket or access point policies: ❌ Off
   - Block public and cross-account access to buckets and objects through any public bucket or access point policies: ❌ Off

---

## 📋 Deployment Steps

### Step 1: Commit Latest Changes
```bash
git add .
git commit -m "feat: S3 integration with fallback to local storage"
git push origin dev
```

### Step 2: Add Environment Variables in Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service: `quickvendor-backend`
3. Go to Environment tab
4. Add the AWS credentials (NEW ones!)

### Step 3: Deploy
1. Either trigger manual deploy in Render
2. Or push to your deployment branch

### Step 4: Verify Deployment
After deployment, test S3 functionality:

```bash
# 1. Check S3 status (replace with your actual token)
curl -X GET https://quickvendor-backend.onrender.com/api/products/s3/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response if S3 is configured:
{
  "status": "connected",
  "bucket_configured": true,
  "message": "S3 service is properly configured and accessible",
  "bucket_name": "quickvendor-products",
  "region": "eu-north-1",
  "storage_type": "s3"
}
```

---

## ✅ Post-Deployment Testing

### Test S3 Upload on Production

1. **Register/Login** to get a token
2. **Create a product with image**
3. **Verify the image URL** starts with `https://quickvendor-products.s3.eu-north-1.amazonaws.com/`
4. **Check S3 bucket** to confirm the image is there
5. **Access the image URL** directly in browser to ensure it's publicly accessible

---

## 🔍 Troubleshooting

### If S3 is not working on Render:

1. **Check Render logs**:
   ```
   Look for: "S3 client initialized successfully for bucket: quickvendor-products"
   Or error: "S3 not configured - missing required AWS environment variables"
   ```

2. **Verify environment variables are set**:
   - Check Render dashboard → Environment tab
   - Ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are present

3. **Test S3 connection**:
   - Use the `/api/products/s3/status` endpoint
   - Check the response for error messages

4. **Fallback behavior**:
   - If S3 fails, the app will automatically use local storage
   - This ensures your app keeps working even if S3 has issues

---

## 🎯 Expected Behavior After Deployment

When everything is configured correctly:

1. ✅ Product images upload to S3 bucket
2. ✅ S3 URLs are saved in database (e.g., `https://quickvendor-products.s3.eu-north-1.amazonaws.com/product-images/...`)
3. ✅ Images are publicly accessible via their S3 URLs
4. ✅ If S3 fails, system falls back to local storage automatically
5. ✅ Status endpoint reports `"status": "connected"` and `"storage_type": "s3"`

---

## 🔒 Security Notes

1. **NEVER commit AWS credentials to Git**
2. **Rotate credentials immediately if exposed**
3. **Use environment variables in Render dashboard**
4. **Monitor AWS billing** to detect unusual activity
5. **Set up CloudWatch alarms** for bucket activity

---

## 📊 Monitoring

After deployment, monitor:

1. **Render Logs** - Check for S3 initialization messages
2. **AWS S3 Console** - Verify new images appear in bucket
3. **Database** - Confirm S3 URLs are being saved
4. **Sentry** - Monitor for any S3-related errors

---

## ✅ Success Criteria

Your S3 integration is working correctly when:

- [ ] Products created on Render have S3 URLs in database
- [ ] Images are visible when accessing S3 URLs
- [ ] S3 status endpoint shows "connected"
- [ ] New images appear in S3 bucket within seconds
- [ ] No S3-related errors in logs

---

**Remember:** The system has automatic fallback to local storage, so your application will continue working even if S3 configuration has issues!
