#!/bin/bash

# QuickVendor Test Runner
# Runs both frontend and backend tests

set -e

echo "🧪 QuickVendor Test Suite Runner"
echo "================================"

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
    if pytest tests/backend/ -v --tb=short; then
        print_status "✅ Backend tests passed!" "${GREEN}"
    else
        print_status "❌ Backend tests failed!" "${RED}"
        BACKEND_FAILED=1
    fi
    
    cd ..
    echo
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "🎨 Running Frontend Tests (React + Vitest)" "${YELLOW}"
    echo "----------------------------------------"
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..." "${YELLOW}"
        npm install
    fi
    
    # Run tests
    if npm run test -- --run; then
        print_status "✅ Frontend tests passed!" "${GREEN}"
    else
        print_status "❌ Frontend tests failed!" "${RED}"
        FRONTEND_FAILED=1
    fi
    
    cd ..
    echo
}

# Initialize failure flags
BACKEND_FAILED=0
FRONTEND_FAILED=0

# Parse command line arguments
case "${1:-all}" in
    "backend"|"be")
        run_backend_tests
        ;;
    "frontend"|"fe")
        run_frontend_tests
        ;;
    "all"|*)
        run_backend_tests
        run_frontend_tests
        ;;
esac

# Print final results
echo "================================"
if [ $BACKEND_FAILED -eq 0 ] && [ $FRONTEND_FAILED -eq 0 ]; then
    print_status "🎉 All tests passed successfully!" "${GREEN}"
    exit 0
else
    if [ $BACKEND_FAILED -eq 1 ]; then
        print_status "❌ Backend tests failed" "${RED}"
    fi
    if [ $FRONTEND_FAILED -eq 1 ]; then
        print_status "❌ Frontend tests failed" "${RED}"
    fi
    print_status "💥 Some tests failed. Check output above." "${RED}"
    exit 1
fi
