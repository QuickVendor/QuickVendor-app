#!/usr/bin/env python3
"""
Verify S3 configuration in production
Run this on Render to check if S3 is properly configured
"""
import os
import sys

print("=" * 60)
print("S3 CONFIGURATION CHECK FOR PRODUCTION")
print("=" * 60)

# Check environment
print("\n1. Environment Check:")
print(f"   RENDER: {os.getenv('RENDER', 'Not set')}")
print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")

# Check AWS credentials
print("\n2. AWS Credentials Check:")
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket = os.getenv('S3_BUCKET_NAME')

print(f"   AWS_ACCESS_KEY_ID: {'Set' if aws_key else 'NOT SET'} {f'({aws_key[:10]}...)' if aws_key else ''}")
print(f"   AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret else 'NOT SET'}")
print(f"   AWS_REGION: {aws_region if aws_region else 'NOT SET'}")
print(f"   S3_BUCKET_NAME: {s3_bucket if s3_bucket else 'NOT SET'}")

# Check boto3
print("\n3. Boto3 Check:")
try:
    import boto3
    print("   ✅ boto3 is installed")
    print(f"   Version: {boto3.__version__}")
except ImportError:
    print("   ❌ boto3 is NOT installed")
    print("   Run: pip install boto3")

# Check S3Manager
print("\n4. S3Manager Check:")
try:
    # Add backend directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app.services.s3_manager import S3Manager, get_s3_manager
    
    s3_manager = get_s3_manager()
    is_configured = s3_manager.is_s3_configured()
    
    print(f"   S3Manager initialized: Yes")
    print(f"   S3 configured: {is_configured}")
    
    if is_configured:
        print(f"   ✅ S3 is ready for uploads")
        print(f"   Bucket: {s3_manager.bucket_name}")
        print(f"   Region: {s3_manager.aws_region}")
        
        # Try to list bucket contents
        try:
            s3_client = s3_manager.s3_client
            response = s3_client.list_objects_v2(
                Bucket=s3_manager.bucket_name,
                MaxKeys=1
            )
            print(f"   ✅ Can access S3 bucket")
        except Exception as e:
            print(f"   ❌ Cannot access S3 bucket: {e}")
    else:
        print(f"   ❌ S3 is NOT configured")
        print(f"   Images will fall back to local storage")
        
except ImportError as e:
    print(f"   ❌ Cannot import S3Manager: {e}")
except Exception as e:
    print(f"   ❌ Error checking S3Manager: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
if aws_key and aws_secret and s3_bucket:
    print("✅ AWS credentials are set")
else:
    print("❌ AWS credentials are missing - S3 won't work!")
    print("\nTO FIX:")
    print("1. Go to Render Dashboard")
    print("2. Navigate to your backend service")
    print("3. Go to Environment tab")
    print("4. Add these environment variables:")
    print("   - AWS_ACCESS_KEY_ID: Your AWS access key")
    print("   - AWS_SECRET_ACCESS_KEY: Your AWS secret key")
    
print("=" * 60)
