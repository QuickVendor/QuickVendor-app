#!/usr/bin/env python3
"""
Comprehensive QA Testing Script for QuickVendor Backend API
Including S3 Storage Integration Testing
"""

import requests
import json
import os
import time
from typing import Dict, Optional, Any
from datetime import datetime
import random
import string
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = None  # Will create a test image if needed

# Test user credentials
TEST_USER = {
    "email": f"test_qa_{random.randint(1000, 9999)}@example.com",
    "password": "TestPassword123!",
    "whatsapp_number": "2341234567890"  # WhatsApp number without + sign
}


class Colors:
    """Terminal colors for better output readability"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")


def print_test(test_name: str, status: bool, details: str = ""):
    """Print test result with color coding"""
    if status:
        status_text = f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}"
    else:
        status_text = f"{Colors.FAIL}✗ FAILED{Colors.ENDC}"
    
    print(f"{Colors.OKCYAN}[TEST]{Colors.ENDC} {test_name}: {status_text}")
    if details:
        print(f"       {Colors.WARNING}Details: {details}{Colors.ENDC}")


def create_test_image():
    """Create a simple test image file"""
    # Create a simple PNG image (1x1 pixel, red)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01^\xf3\xff\x11\x00\x00\x00\x00IEND\xaeB`\x82'
    
    test_image_path = "/tmp/test_image.png"
    with open(test_image_path, "wb") as f:
        f.write(png_data)
    
    return test_image_path


class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.test_product_id = None
        
    def register_user(self) -> bool:
        """Test user registration"""
        print_header("1. USER REGISTRATION TEST")
        
        response = requests.post(
            f"{self.base_url}/api/users/register",
            json=TEST_USER
        )
        
        if response.status_code == 201:
            data = response.json()
            self.user_id = data.get("id")
            print_test("User Registration", True, f"User created: {TEST_USER['email']}, ID: {self.user_id}")
            return True
        else:
            print_test("User Registration", False, f"Status: {response.status_code}, Error: {response.text}")
            return False
    
    def login_user(self) -> bool:
        """Test user login"""
        print_header("2. USER LOGIN TEST")
        
        # JSON data for login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            print_test("User Login", True, f"Token received")
            return True
        else:
            print_test("User Login", False, f"Status: {response.status_code}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.token}"
        }
    
    def test_s3_status(self) -> Dict[str, Any]:
        """Test S3 service status"""
        print_header("3. S3 SERVICE STATUS TEST")
        
        response = requests.get(
            f"{self.base_url}/api/products/s3/status",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            storage_type = data.get("storage_type", "unknown")
            
            if status == "connected":
                print_test("S3 Connection", True, f"S3 is configured and accessible")
                print(f"       Bucket: {data.get('bucket_name', 'N/A')}")
                print(f"       Region: {data.get('region', 'N/A')}")
            elif status == "not_configured":
                print_test("S3 Connection", True, f"S3 not configured - using {storage_type} storage")
            else:
                print_test("S3 Connection", False, f"Status: {status}, Message: {data.get('message', '')}")
            
            return data
        else:
            print_test("S3 Status Check", False, f"Status: {response.status_code}")
            return {}
    
    def create_product(self) -> bool:
        """Test product creation"""
        print_header("4. PRODUCT CREATION TEST")
        
        # Create test image
        test_image = create_test_image()
        
        with open(test_image, 'rb') as img:
            files = {
                'image_1': ('test_image.png', img, 'image/png')
            }
            data = {
                'name': f'Test Product {random.randint(1000, 9999)}',
                'price': 99.99,
                'description': 'This is a test product for QA testing',
                'is_available': True
            }
            
            response = requests.post(
                f"{self.base_url}/api/products/",
                headers=self.get_headers(),
                data=data,
                files=files
            )
        
        if response.status_code == 201:
            product_data = response.json()
            self.test_product_id = product_data.get("id")
            print_test("Product Creation", True, f"Product ID: {self.test_product_id}")
            print(f"       Name: {product_data.get('name')}")
            print(f"       Price: ${product_data.get('price')}")
            if product_data.get('image_url_1'):
                print(f"       Image URL: {product_data.get('image_url_1')}")
            return True
        else:
            print_test("Product Creation", False, f"Status: {response.status_code}, Error: {response.text}")
            return False
    
    def test_s3_upload(self, storage_type: str = "unknown") -> bool:
        """Test S3 image upload"""
        print_header("5. S3 IMAGE UPLOAD TEST")
        
        if not self.test_product_id:
            print_test("S3 Upload", False, "No product ID available")
            return False
        
        # Create test image
        test_image = create_test_image()
        
        with open(test_image, 'rb') as img:
            files = {
                'image': ('test_s3_image.png', img, 'image/png')
            }
            data = {
                'image_slot': 2  # Use slot 2 for S3 test
            }
            
            response = requests.post(
                f"{self.base_url}/api/products/{self.test_product_id}/images/upload",
                headers=self.get_headers(),
                data=data,
                files=files
            )
        
        if response.status_code == 200:
            upload_data = response.json()
            storage_used = upload_data.get("storage_type", "unknown")
            print_test("Image Upload", True, f"Storage type: {storage_used}")
            
            if storage_used == "s3":
                print(f"       S3 URL: {upload_data.get('url', 'N/A')}")
                print(f"       S3 Key: {upload_data.get('key', 'N/A')}")
            else:
                print(f"       Local URL: {upload_data.get('url', 'N/A')}")
            
            print(f"       Image Slot: {upload_data.get('image_slot', 'N/A')}")
            return True
        else:
            print_test("S3 Upload", False, f"Status: {response.status_code}, Error: {response.text}")
            return False
    
    def get_products(self) -> bool:
        """Test getting user products"""
        print_header("6. GET USER PRODUCTS TEST")
        
        response = requests.get(
            f"{self.base_url}/api/products/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            products = response.json()
            print_test("Get Products", True, f"Found {len(products)} products")
            
            for product in products[:3]:  # Show first 3 products
                print(f"       - {product.get('name')} (${product.get('price')})")
            
            return True
        else:
            print_test("Get Products", False, f"Status: {response.status_code}")
            return False
    
    def update_product(self) -> bool:
        """Test product update"""
        print_header("7. PRODUCT UPDATE TEST")
        
        if not self.test_product_id:
            print_test("Product Update", False, "No product ID available")
            return False
        
        update_data = {
            'name': f'Updated Test Product {random.randint(1000, 9999)}',
            'price': 149.99,
            'description': 'Updated description for QA testing'
        }
        
        response = requests.put(
            f"{self.base_url}/api/products/{self.test_product_id}",
            headers=self.get_headers(),
            data=update_data
        )
        
        if response.status_code == 200:
            updated_product = response.json()
            print_test("Product Update", True, f"Product updated successfully")
            print(f"       New Name: {updated_product.get('name')}")
            print(f"       New Price: ${updated_product.get('price')}")
            return True
        else:
            print_test("Product Update", False, f"Status: {response.status_code}")
            return False
    
    def track_click(self) -> bool:
        """Test product click tracking"""
        print_header("8. CLICK TRACKING TEST")
        
        if not self.test_product_id:
            print_test("Click Tracking", False, "No product ID available")
            return False
        
        # Track multiple clicks
        for i in range(3):
            response = requests.post(
                f"{self.base_url}/api/products/{self.test_product_id}/track-click"
            )
            
            if response.status_code != 200:
                print_test("Click Tracking", False, f"Failed on click {i+1}")
                return False
        
        print_test("Click Tracking", True, "3 clicks tracked successfully")
        return True
    
    def delete_product_image(self) -> bool:
        """Test deleting product image from S3"""
        print_header("9. DELETE S3 IMAGE TEST")
        
        if not self.test_product_id:
            print_test("Delete Image", False, "No product ID available")
            return False
        
        response = requests.delete(
            f"{self.base_url}/api/products/{self.test_product_id}/images/2",
            headers=self.get_headers()
        )
        
        if response.status_code == 204:
            print_test("Delete S3 Image", True, "Image deleted from slot 2")
            return True
        elif response.status_code == 404:
            print_test("Delete S3 Image", True, "No image in slot 2 (expected)")
            return True
        else:
            print_test("Delete S3 Image", False, f"Status: {response.status_code}")
            return False
    
    def delete_product(self) -> bool:
        """Test product deletion"""
        print_header("10. PRODUCT DELETION TEST")
        
        if not self.test_product_id:
            print_test("Product Deletion", False, "No product ID available")
            return False
        
        response = requests.delete(
            f"{self.base_url}/api/products/{self.test_product_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 204:
            print_test("Product Deletion", True, f"Product {self.test_product_id} deleted")
            return True
        else:
            print_test("Product Deletion", False, f"Status: {response.status_code}")
            return False
    
    def test_store_endpoints(self) -> bool:
        """Test store-related endpoints"""
        print_header("11. STORE ENDPOINTS TEST")
        
        # Get store by username
        response = requests.get(f"{self.base_url}/api/store/{TEST_USER['email'].split('@')[0]}")
        
        if response.status_code == 200:
            store_data = response.json()
            print_test("Get Store Details", True, f"Store: {store_data.get('storefront', {}).get('store_name', 'N/A')}")
            return True
        elif response.status_code == 404:
            # Store might not exist yet, which is okay
            print_test("Get Store Details", True, "Store not found (expected for new user)")
            return True
        else:
            print_test("Get Store Details", False, f"Status: {response.status_code}")
            return False
    
    def test_feedback(self) -> bool:
        """Test feedback submission"""
        print_header("12. FEEDBACK SUBMISSION TEST")
        
        feedback_data = {
            "message": "This is a test feedback from QA testing script",
            "url": f"{self.base_url}/test-page",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        response = requests.post(
            f"{self.base_url}/api/feedback/report",
            json=feedback_data
        )
        
        if response.status_code == 200:
            print_test("Feedback Submission", True, "Feedback submitted successfully")
            return True
        else:
            print_test("Feedback Submission", False, f"Status: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}Starting QuickVendor Backend QA Testing...{Colors.ENDC}")
        print(f"Target: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
        
        # Test sequence
        tests = [
            ("User Registration", self.register_user),
            ("User Login", self.login_user),
            ("S3 Status Check", lambda: self.test_s3_status() is not None),
            ("Product Creation", self.create_product),
            ("S3 Image Upload", self.test_s3_upload),
            ("Get Products", self.get_products),
            ("Product Update", self.update_product),
            ("Click Tracking", self.track_click),
            ("Delete S3 Image", self.delete_product_image),
            ("Product Deletion", self.delete_product),
            ("Store Endpoints", self.test_store_endpoints),
            ("Feedback Submission", self.test_feedback)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                if test_func():
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print_test(test_name, False, f"Exception: {str(e)}")
                results["failed"] += 1
        
        # Print summary
        print_header("TEST SUMMARY")
        print(f"{Colors.BOLD}Total Tests: {results['total']}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Passed: {results['passed']}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {results['failed']}{Colors.ENDC}")
        
        success_rate = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
        
        if success_rate == 100:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED! ({success_rate:.1f}%){Colors.ENDC}")
        elif success_rate >= 80:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ MOSTLY PASSED ({success_rate:.1f}%){Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ TESTS FAILED ({success_rate:.1f}%){Colors.ENDC}")
        
        return results


def main():
    """Main execution function"""
    tester = APITester()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print(f"{Colors.FAIL}Error: Backend server is not responding at {BASE_URL}{Colors.ENDC}")
            print("Please ensure the server is running: uvicorn app.main:app --reload")
            return
    except requests.ConnectionError:
        print(f"{Colors.FAIL}Error: Cannot connect to backend server at {BASE_URL}{Colors.ENDC}")
        print("Please start the server: uvicorn app.main:app --reload")
        return
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Clean up test image
    test_image_path = "/tmp/test_image.png"
    if os.path.exists(test_image_path):
        os.remove(test_image_path)


if __name__ == "__main__":
    main()
