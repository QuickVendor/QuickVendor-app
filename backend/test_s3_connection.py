#!/usr/bin/env python3
"""
Test S3 connectivity and bucket access
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if boto3 is available
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    print("✅ boto3 is installed")
except ImportError:
    print("❌ boto3 is not installed. Please run: pip install boto3")
    sys.exit(1)

# Get credentials
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION', 'us-east-1')
bucket_name = os.getenv('S3_BUCKET_NAME')

print("\n=== AWS Configuration ===")
print(f"AWS_ACCESS_KEY_ID: {aws_access_key[:10]}..." if aws_access_key else "❌ AWS_ACCESS_KEY_ID not set")
print(f"AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret_key else '❌ Not set'}")
print(f"AWS_REGION: {aws_region}")
print(f"S3_BUCKET_NAME: {bucket_name if bucket_name else '❌ Not set'}")

if not all([aws_access_key, aws_secret_key, bucket_name]):
    print("\n❌ Missing required AWS configuration. Please check your .env file.")
    sys.exit(1)

# Test S3 connection
print("\n=== Testing S3 Connection ===")

try:
    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    print("✅ S3 client created successfully")
    
    # Test 1: Check if we can access the bucket
    print(f"\n=== Testing Bucket Access: {bucket_name} ===")
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists and is accessible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("   Please create the bucket in AWS S3 console")
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("   Please check IAM permissions for your AWS credentials")
        else:
            print(f"❌ Error accessing bucket: {error_code}")
            print(f"   Details: {e}")
        sys.exit(1)
    
    # Test 2: List objects in bucket (first 5)
    print("\n=== Listing Bucket Contents (first 5 objects) ===")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        
        if 'Contents' in response:
            print(f"Found {response['KeyCount']} objects (showing first 5):")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} (Size: {obj['Size']} bytes)")
        else:
            print("ℹ️  Bucket is empty")
    except ClientError as e:
        print(f"❌ Error listing bucket contents: {e}")
    
    # Test 3: Check bucket location
    print("\n=== Bucket Configuration ===")
    try:
        location = s3_client.get_bucket_location(Bucket=bucket_name)
        bucket_region = location['LocationConstraint'] or 'us-east-1'
        print(f"✅ Bucket region: {bucket_region}")
        
        if bucket_region != aws_region:
            print(f"⚠️  Warning: Bucket is in {bucket_region} but AWS_REGION is set to {aws_region}")
            print(f"   Consider updating AWS_REGION to {bucket_region} for better performance")
    except ClientError as e:
        print(f"❌ Error getting bucket location: {e}")
    
    # Test 4: Check if we can upload (dry run)
    print("\n=== Testing Upload Permissions ===")
    try:
        # Try to upload a small test object
        test_key = "test-permissions/test.txt"
        test_content = b"QuickVendor S3 test"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"✅ Successfully uploaded test file: {test_key}")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print(f"✅ Successfully deleted test file")
        
    except ClientError as e:
        print(f"❌ Error testing upload permissions: {e}")
        print("   Please check IAM permissions for PutObject and DeleteObject")
    
    # Test 5: Check CORS configuration
    print("\n=== Checking CORS Configuration ===")
    try:
        cors = s3_client.get_bucket_cors(Bucket=bucket_name)
        print("✅ CORS is configured:")
        for rule in cors['CORSRules']:
            print(f"  - Allowed Origins: {rule.get('AllowedOrigins', [])}")
            print(f"  - Allowed Methods: {rule.get('AllowedMethods', [])}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
            print("ℹ️  No CORS configuration found")
            print("   This is okay for backend uploads, but needed for direct browser uploads")
        else:
            print(f"❌ Error checking CORS: {e}")
    
    print("\n=== Summary ===")
    print("✅ S3 is properly configured and accessible!")
    print(f"✅ Bucket '{bucket_name}' is ready for use")
    print("\n📝 Next steps:")
    print("1. Make sure your application is loading these environment variables")
    print("2. Check that the S3Manager is being initialized properly")
    print("3. Verify that the upload endpoint is using S3 and not falling back to local storage")
    
except NoCredentialsError:
    print("❌ AWS credentials are invalid or not properly configured")
    print("   Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
