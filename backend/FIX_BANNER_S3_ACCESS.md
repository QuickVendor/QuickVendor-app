# 🔓 Fix Banner Images Not Displaying - S3 Public Access

## Problem
Banner images are uploading to S3 but can't be viewed because the bucket policy only allows public access to product images, not banner images.

## Solution: Update S3 Bucket Policy for Banner Images

### Step 1: Go to AWS S3 Console
1. Open https://s3.console.aws.amazon.com/
2. Click on your bucket: `quickvendor-products`

### Step 2: Update Bucket Policy
1. Go to **Permissions** tab
2. Scroll to **Bucket policy** section
3. Click **Edit**
4. Replace the existing policy with this updated policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadProductImages",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::quickvendor-products/qv-products-img/*"
        },
        {
            "Sid": "PublicReadBannerImages",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::quickvendor-products/store-banners/*"
        }
    ]
}
```

5. Click **Save changes**

### Step 3: Verify It Works
After uploading a banner image:
1. Try accessing the banner image URL directly in your browser
2. The image should display instead of showing "Access Denied"

## Testing the Fix
1. Upload a banner image through the frontend
2. Check the API response includes the banner URL
3. Access the banner URL directly to confirm it's publicly accessible
4. Verify the banner displays in both:
   - Custom settings section
   - Public storefront

## Technical Details
- Product images are stored in: `qv-products-img/{product_id}/filename.jpg`
- Banner images are stored in: `store-banners/{user_id}/filename.jpg`
- Both paths need public read access for images to display in the frontend
