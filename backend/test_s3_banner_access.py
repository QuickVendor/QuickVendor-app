#!/usr/bin/env python3
"""
Test script to verify S3 banner access configuration
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_s3_access():
    """Test S3 bucket access and configuration"""
    
    bucket_name = os.getenv('S3_BUCKET_NAME', 'quickvendor-products')
    region = os.getenv('AWS_REGION', 'eu-north-1')
    
    print("=== S3 Configuration Test ===")
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print()
    
    # Test bucket access
    bucket_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/"
    
    try:
        response = requests.get(bucket_url, timeout=10)
        print(f"Bucket access test: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Bucket is publicly accessible")
        elif response.status_code == 403:
            print("⚠️  Bucket access forbidden - this is normal if bucket policy is restrictive")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing bucket access: {e}")
    
    print()
    print("=== Required Folder Structure ===")
    print("Your bucket should allow public read access to:")
    print(f"  📁 {bucket_name}/qv-products-img/* (product images)")
    print(f"  📁 {bucket_name}/store-banners/* (banner images)")
    print()
    
    print("=== Next Steps ===")
    print("1. Apply the bucket policy from FIX_BANNER_S3_ACCESS.md")
    print("2. Upload a test banner image through your frontend")
    print("3. Check if the banner URL is publicly accessible")
    print("4. Verify banner displays in the storefront")

if __name__ == "__main__":
    test_s3_access()
