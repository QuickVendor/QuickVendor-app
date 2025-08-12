#!/usr/bin/env python3
"""
Test S3Manager initialization
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.s3_manager import S3Manager
    
    print("Testing S3Manager initialization...")
    print("-" * 50)
    
    # Initialize S3Manager
    s3_manager = S3Manager()
    
    # Check configuration
    print(f"boto3 available: {s3_manager.is_configured if hasattr(s3_manager, 'is_configured') else 'Unknown'}")
    print(f"S3 configured: {s3_manager.is_s3_configured()}")
    
    if s3_manager.is_s3_configured():
        print(f"✅ S3Manager is properly configured!")
        print(f"   Bucket: {s3_manager.bucket_name}")
        print(f"   Region: {s3_manager.aws_region}")
    else:
        print("❌ S3Manager is NOT configured properly")
        print("   This means uploads will fall back to local storage")
        
except ImportError as e:
    print(f"❌ Error importing S3Manager: {e}")
except Exception as e:
    print(f"❌ Error initializing S3Manager: {e}")
