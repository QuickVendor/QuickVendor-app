#!/bin/bash

# QuickVendor Test Runner
# Runs backend tests

set -e

echo "🧪 QuickVendor Backend Test Suite Runner"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to run backend tests
run_backend_tests() {
    print_status "📊 Running Backend Tests (FastAPI + Pytest)" "${YELLOW}"
    echo "----------------------------------------"
    
    cd backend
    
    # Check if test dependencies are installed
    if ! pip list | grep -q "pytest"; then
        print_status "Installing test dependencies..." "${YELLOW}"
        pip install -r requirements-test.txt
    fi
    
    # Run tests
    if pytest tests/ -v --tb=short; then
        print_status "✅ Backend tests passed!" "${GREEN}"
    else
        print_status "❌ Backend tests failed!" "${RED}"
        BACKEND_FAILED=1
    fi
    
    cd ..
    echo
}

# Initialize failure flags
BACKEND_FAILED=0

# Run backend tests
run_backend_tests

# Print final results
echo "================================"
if [ $BACKEND_FAILED -eq 0 ]; then
    print_status "🎉 All tests passed successfully!" "${GREEN}"
    exit 0
else
    print_status "❌ Backend tests failed" "${RED}"
    print_status "💥 Tests failed. Check output above." "${RED}"
    exit 1
fi
