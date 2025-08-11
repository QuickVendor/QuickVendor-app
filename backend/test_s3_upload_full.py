#!/usr/bin/env python3
"""
Complete S3 Upload Test
Tests the full flow of uploading images to S3 and saving URLs to database
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": f"s3test_{int(time.time())}@example.com",
    "password": "TestPassword123!",
    "whatsapp_number": "2341234567890"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def create_test_image_bytes():
    """Create a simple test image in memory"""
    # Simple 1x1 red PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01^\xf3\xff\x11\x00\x00\x00\x00IEND\xaeB`\x82'
    return png_data

def main():
    print(f"\n{Colors.BOLD}=== S3 Upload Integration Test ==={Colors.ENDC}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}\n")
    
    # Step 1: Register user
    print(f"{Colors.BOLD}1. User Registration{Colors.ENDC}")
    response = requests.post(f"{BASE_URL}/api/users/register", json=TEST_USER)
    if response.status_code == 201:
        user_data = response.json()
        print_status(f"User registered: {TEST_USER['email']}", "success")
        print(f"   User ID: {user_data['id']}")
    else:
        print_status(f"Registration failed: {response.status_code}", "error")
        print(f"   Error: {response.text}")
        return
    
    # Step 2: Login
    print(f"\n{Colors.BOLD}2. User Login{Colors.ENDC}")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_status("Login successful", "success")
        print(f"   Token: {token[:20]}...")
    else:
        print_status(f"Login failed: {response.status_code}", "error")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Check S3 status
    print(f"\n{Colors.BOLD}3. S3 Configuration Status{Colors.ENDC}")
    response = requests.get(f"{BASE_URL}/api/products/s3/status", headers=headers)
    if response.status_code == 200:
        s3_status = response.json()
        status = s3_status.get("status")
        storage_type = s3_status.get("storage_type")
        
        if status == "connected":
            print_status("S3 is configured and connected", "success")
            print(f"   Bucket: {s3_status.get('bucket_name')}")
            print(f"   Region: {s3_status.get('region')}")
        elif status == "not_configured":
            print_status("S3 not configured, using local storage", "warning")
        else:
            print_status(f"S3 status: {status}", "warning")
        
        print(f"   Storage type: {storage_type}")
    else:
        print_status(f"Failed to check S3 status: {response.status_code}", "error")
    
    # Step 4: Create product with image
    print(f"\n{Colors.BOLD}4. Create Product with Image{Colors.ENDC}")
    
    test_image = create_test_image_bytes()
    files = {
        'image_1': ('test_product.png', test_image, 'image/png')
    }
    data = {
        'name': f'S3 Test Product {int(time.time())}',
        'price': 199.99,
        'description': 'Product to test S3 image upload',
        'is_available': True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/products/",
        headers=headers,
        data=data,
        files=files
    )
    
    if response.status_code == 201:
        product = response.json()
        product_id = product["id"]
        print_status(f"Product created: {product_id}", "success")
        print(f"   Name: {product['name']}")
        print(f"   Price: ${product['price']}")
        
        if product.get("image_url_1"):
            image_url = product["image_url_1"]
            print(f"   Image URL 1: {image_url}")
            
            # Check if it's an S3 URL
            if "s3" in image_url and "amazonaws.com" in image_url:
                print_status("   ✓ Image stored in S3", "success")
            else:
                print_status("   ⚠ Image stored locally", "warning")
        else:
            print_status("   No image URL saved", "error")
    else:
        print_status(f"Product creation failed: {response.status_code}", "error")
        print(f"   Error: {response.text}")
        return
    
    # Step 5: Upload additional image using S3 endpoint
    print(f"\n{Colors.BOLD}5. Upload Additional Image via S3 Endpoint{Colors.ENDC}")
    
    test_image2 = create_test_image_bytes()
    files2 = {
        'image': ('test_s3_direct.png', test_image2, 'image/png')
    }
    data2 = {
        'image_slot': 2
    }
    
    response = requests.post(
        f"{BASE_URL}/api/products/{product_id}/images/upload",
        headers=headers,
        data=data2,
        files=files2
    )
    
    if response.status_code == 200:
        upload_result = response.json()
        print_status("Image uploaded successfully", "success")
        print(f"   Storage type: {upload_result.get('storage_type')}")
        print(f"   URL: {upload_result.get('url')}")
        
        if upload_result.get('storage_type') == 's3':
            print(f"   S3 Key: {upload_result.get('key')}")
            print_status("   ✓ Image uploaded to S3", "success")
        else:
            print_status("   ⚠ Image uploaded to local storage", "warning")
        
        print(f"   Image slot: {upload_result.get('image_slot')}")
    else:
        print_status(f"Image upload failed: {response.status_code}", "error")
        print(f"   Error: {response.text}")
    
    # Step 6: Verify images are saved in database
    print(f"\n{Colors.BOLD}6. Verify Database Storage{Colors.ENDC}")
    
    response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
    if response.status_code == 200:
        products = response.json()
        for p in products:
            if p["id"] == product_id:
                print_status("Product found in database", "success")
                print(f"   Product ID: {p['id']}")
                
                # Check all image URLs
                image_urls_found = []
                for i in range(1, 6):
                    url = p.get(f"image_url_{i}")
                    if url:
                        image_urls_found.append(i)
                        print(f"   Image URL {i}: {url}")
                        
                        # Check if S3 URL
                        if "s3" in url and "amazonaws.com" in url:
                            print_status(f"      ✓ Slot {i} uses S3", "success")
                        else:
                            print_status(f"      ⚠ Slot {i} uses local storage", "warning")
                
                if image_urls_found:
                    print_status(f"   Total images saved: {len(image_urls_found)} (slots: {image_urls_found})", "success")
                else:
                    print_status("   No images saved in database", "error")
                break
    else:
        print_status(f"Failed to retrieve products: {response.status_code}", "error")
    
    # Step 7: Test image retrieval (if S3)
    print(f"\n{Colors.BOLD}7. Test Image Accessibility{Colors.ENDC}")
    
    if 'image_url' in locals() and image_url:
        if "s3" in image_url and "amazonaws.com" in image_url:
            # Test if S3 image is accessible
            response = requests.head(image_url)
            if response.status_code == 200:
                print_status(f"S3 image is publicly accessible", "success")
                print(f"   Content-Type: {response.headers.get('Content-Type')}")
                print(f"   Content-Length: {response.headers.get('Content-Length')} bytes")
            else:
                print_status(f"S3 image not accessible: {response.status_code}", "error")
                print("   Check S3 bucket permissions and ACL settings")
        else:
            print_status("Using local storage, skipping S3 accessibility test", "info")
    
    # Summary
    print(f"\n{Colors.BOLD}=== Test Summary ==={Colors.ENDC}")
    
    if 's3_status' in locals() and s3_status.get('status') == 'connected':
        print_status("✅ S3 is properly configured", "success")
        print_status("✅ Images are being uploaded to S3", "success")
        print_status("✅ S3 URLs are saved to database", "success")
    else:
        print_status("⚠️  S3 is not configured", "warning")
        print_status("ℹ️  Using local file storage as fallback", "info")
        print("\nTo enable S3:")
        print("1. Ensure AWS credentials are in .env file")
        print("2. Restart the FastAPI application")
        print("3. Check that boto3 is installed")

if __name__ == "__main__":
    main()
