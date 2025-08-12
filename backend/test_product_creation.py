#!/usr/bin/env python3
"""
Test product creation with S3 image upload
"""
import os
import sys
import asyncio
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_product_creation():
    try:
        from app.services.s3_manager import S3Manager, get_s3_manager
        
        print("=" * 60)
        print("Testing Product Image Upload to S3")
        print("=" * 60)
        
        # Test S3Manager singleton
        s3_manager = get_s3_manager()
        print(f"\n1. S3Manager Status:")
        print(f"   - Configured: {s3_manager.is_s3_configured()}")
        print(f"   - Bucket: {s3_manager.bucket_name}")
        print(f"   - Region: {s3_manager.aws_region}")
        
        if not s3_manager.is_s3_configured():
            print("\n❌ S3 is not configured! Images will use local storage.")
            print("   Check that boto3 is installed and AWS credentials are set.")
            return
        
        # Create a test image (small PNG)
        print(f"\n2. Creating test image...")
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82'
        test_image = BytesIO(test_image_data)
        
        # Test upload
        print(f"\n3. Testing upload to S3...")
        test_product_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            result = await s3_manager.upload_product_image(
                file_content=test_image,
                filename="test_image.png",
                product_id=test_product_id,
                content_type="image/png"
            )
            
            print(f"\n✅ Upload successful!")
            print(f"   - URL: {result['url']}")
            print(f"   - Key: {result['key']}")
            print(f"   - Filename: {result['filename']}")
            
            # Try to verify the file exists
            if s3_manager.s3_client:
                try:
                    s3_manager.s3_client.head_object(
                        Bucket=s3_manager.bucket_name,
                        Key=result['key']
                    )
                    print(f"\n✅ File verified in S3!")
                    
                    # Clean up test file
                    s3_manager.s3_client.delete_object(
                        Bucket=s3_manager.bucket_name,
                        Key=result['key']
                    )
                    print(f"   - Test file cleaned up")
                except Exception as e:
                    print(f"\n⚠️  Could not verify file: {e}")
                    
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
if __name__ == "__main__":
    asyncio.run(test_product_creation())
