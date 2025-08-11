# AWS S3 Integration Setup Guide for Quick Vendor

## Phase 1: AWS IAM Setup Instructions 📝

This guide provides step-by-step instructions for setting up AWS IAM (Identity and Access Management) to securely integrate S3 bucket storage with your Quick Vendor FastAPI backend.

---

## 1. Create a New IAM User with Programmatic Access

### Step 1.1: Access IAM Console
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/)
2. Navigate to **IAM** (Identity and Access Management)
   - You can search for "IAM" in the top search bar
   - Or go directly to: `https://console.aws.amazon.com/iam/`

### Step 1.2: Create New User
1. In the IAM dashboard, click on **Users** in the left sidebar
2. Click the **Create user** button
3. Enter user details:
   - **User name**: `quickvendor-s3-user` (or your preferred name)
   - **Access type**: Check only **Programmatic access**
   - Do NOT check "AWS Management Console access"
4. Click **Next**

### Step 1.3: Skip Permissions (We'll add custom policy later)
1. On the "Set permissions" page, select **Attach policies directly**
2. Don't select any policies yet (we'll create a custom one)
3. Click **Next**

### Step 1.4: Add Tags (Optional)
1. Add any tags if required for your organization
   - Example: `Environment: Production`, `Application: QuickVendor`
2. Click **Next**

### Step 1.5: Review and Create
1. Review the user details
2. Click **Create user**
3. **IMPORTANT**: Save the credentials immediately:
   - **Access key ID**
   - **Secret access key**
   - Click **Download .csv** to save these credentials
   - ⚠️ **Note**: The secret access key won't be shown again!

---

## 2. Create and Attach Custom IAM Policy (Least Privilege)

### Step 2.1: Navigate to Policies
1. In the IAM dashboard, click on **Policies** in the left sidebar
2. Click **Create policy**

### Step 2.2: Define Policy Using JSON
1. Click on the **JSON** tab
2. Replace the default content with the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "QuickVendorS3Access",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/product-images/*"
        },
        {
            "Sid": "ListBucketContents",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME",
            "Condition": {
                "StringLike": {
                    "s3:prefix": [
                        "product-images/*"
                    ]
                }
            }
        }
    ]
}
```

3. **IMPORTANT**: Replace `YOUR-BUCKET-NAME` with your actual S3 bucket name
   - Example: If your bucket is named `quickvendor-assets`, the resource would be:
   - `"Resource": "arn:aws:s3:::quickvendor-assets/product-images/*"`

### Step 2.3: Review and Name Policy
1. Click **Next: Tags**
2. Add tags if needed, then click **Next: Review**
3. Enter policy details:
   - **Name**: `QuickVendorS3ProductImagesPolicy`
   - **Description**: `Allows PutObject, GetObject, and DeleteObject operations only on the product-images folder in the Quick Vendor S3 bucket`
4. Click **Create policy**

### Step 2.4: Attach Policy to IAM User
1. Go back to **Users** in the IAM dashboard
2. Click on the user you created (`quickvendor-s3-user`)
3. Click on the **Permissions** tab
4. Click **Add permissions** → **Attach policies directly**
5. Search for `QuickVendorS3ProductImagesPolicy`
6. Check the checkbox next to your policy
7. Click **Next** → **Add permissions**

---

## 3. Configure Environment Variables on Render

### Step 3.1: Access Render Dashboard
1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Navigate to your FastAPI service

### Step 3.2: Add Environment Variables
1. Click on your FastAPI service
2. Go to the **Environment** tab
3. Add the following environment variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | Your Access Key ID | From Step 1.5 |
| `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key | From Step 1.5 |
| `AWS_REGION` | Your AWS Region | e.g., `us-east-1`, `eu-west-1` |
| `S3_BUCKET_NAME` | Your Bucket Name | e.g., `quickvendor-assets` |

### Step 3.3: Save and Deploy
1. Click **Save Changes**
2. Render will automatically redeploy your service with the new environment variables

---

## 4. Verify Setup (Optional but Recommended)

### Test AWS Credentials
You can verify your setup using the AWS CLI:

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure AWS CLI with your credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region

# Test access to your bucket
aws s3 ls s3://YOUR-BUCKET-NAME/product-images/
```

### Security Best Practices Checklist

- [ ] IAM user has **only programmatic access** (no console access)
- [ ] IAM policy follows **least privilege principle**
- [ ] Permissions are restricted to specific bucket and folder
- [ ] Credentials are stored as **environment variables**, not in code
- [ ] Secret access key is **never committed to version control**
- [ ] Consider enabling **MFA** for the root AWS account
- [ ] Set up **CloudTrail** for auditing S3 access (optional)
- [ ] Enable **S3 bucket versioning** for data protection (optional)

---

## 5. Local Development Setup

For local development, create a `.env` file in your backend directory:

```bash
# .env file (add to .gitignore!)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=your_region_here
S3_BUCKET_NAME=your_bucket_name_here
```

**⚠️ IMPORTANT**: Ensure `.env` is in your `.gitignore` file to prevent credentials from being committed!

---

## Next Steps

After completing this IAM setup:
1. Proceed to Phase 2 for implementing the S3 integration in your FastAPI backend
2. Test the upload functionality with sample images
3. Monitor AWS CloudWatch for any access issues
4. Set up billing alerts to track S3 usage costs

---

## Troubleshooting

### Common Issues and Solutions

1. **Access Denied Error**
   - Verify the bucket name in the policy matches exactly
   - Check that the region is correct
   - Ensure the policy is attached to the user

2. **Invalid Credentials**
   - Regenerate access keys if compromised
   - Verify environment variables are set correctly on Render
   - Check for extra spaces in credential values

3. **Object Not Found**
   - Ensure the `product-images/` folder exists in your bucket
   - Verify the full S3 path in your code

### Support Resources
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
- [Render Environment Variables](https://render.com/docs/environment-variables)

---

*Document Version: 1.0*  
*Last Updated: August 2024*  
*For: Quick Vendor FastAPI Backend S3 Integration*
