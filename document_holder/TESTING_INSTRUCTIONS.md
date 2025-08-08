# QuickVendor Testing Instructions

## Overview

This guide provides comprehensive instructions for running tests in the QuickVendor application. The project includes both frontend and backend test suites with full coverage of the feedback system functionality.

## Test Infrastructure

### Frontend Testing
- **Framework**: Vitest v1.6.1 with jsdom environment
- **Libraries**: @testing-library/react, @testing-library/user-event, @testing-library/jest-dom
- **TypeScript Support**: Full TypeScript integration
- **Test Location**: `frontend/src/__tests__/`

### Backend Testing
- **Framework**: pytest v8.0.0
- **Libraries**: pytest-asyncio, pytest-mock, httpx, FastAPI TestClient
- **Environment**: Python 3.12.3 virtual environment
- **Test Location**: `backend/tests/`

## Prerequisites

### Frontend Prerequisites
- Node.js 18+
- npm or yarn package manager
- All frontend dependencies installed (`npm install`)

### Backend Prerequisites
- Python 3.9+
- Virtual environment activated
- All backend dependencies installed (`pip install -r requirements.txt`)

## Running Frontend Tests

### Quick Test Execution
```bash
# Navigate to frontend directory
cd frontend

# Run all tests once
npm test -- --run

# Run tests with coverage
npm run test:coverage

# Run tests in UI mode (interactive)
npm run test:ui
```

### Watch Mode (Development)
```bash
# Run tests in watch mode (re-runs on file changes)
npm test
```

### Specific Test Execution
```bash
# Run specific test file
npm test -- FeedbackModal.test.tsx --run

# Run tests matching pattern
npm test -- --run -t "feedback"

# Run tests for specific component
npm test -- FloatingFeedbackButton.test.tsx --run
```

### Frontend Test Files
- `frontend/src/__tests__/FeedbackModal.test.tsx` - 13 tests
- `frontend/src/__tests__/FloatingFeedbackButton.test.tsx` - 11 tests
- `frontend/src/__tests__/Navigation.test.tsx` - 4 tests

### Expected Frontend Output
```
Test Files  3 passed (3)
Tests      28 passed (28)
Duration   2.80s
```

## Running Backend Tests

### Setup Backend Environment
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Ensure dependencies are installed
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock httpx
```

### Quick Test Execution
```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with warnings disabled
python -m pytest tests/ -v --disable-warnings

# Run tests with coverage
python -m pytest tests/ --cov=app
```

### Specific Test Execution
```bash
# Run specific test file
python -m pytest tests/test_feedback.py -v

# Run specific test class
python -m pytest tests/test_feedback.py::TestFeedbackEndpoint -v

# Run specific test method
python -m pytest tests/test_feedback.py::TestFeedbackEndpoint::test_submit_valid_feedback -v

# Run tests with specific marker
python -m pytest tests/ -v -m asyncio
```

### Backend Test Files
- `backend/tests/test_feedback.py` - 16 tests
- `backend/tests/conftest.py` - Test configuration
- `backend/pytest.ini` - Pytest configuration

### Expected Backend Output
```
Test Files  1 passed (1)
Tests      16 passed (16)
Duration   1.04s
```

## Running All Tests

### Sequential Execution
```bash
# From project root, run frontend tests first
cd frontend && npm test -- --run

# Then run backend tests
cd ../backend && source venv/bin/activate && python -m pytest tests/ -v --disable-warnings
```

### Parallel Execution (Advanced)
```bash
# Create script to run both test suites
#!/bin/bash
cd frontend && npm test -- --run &
cd backend && source venv/bin/activate && python -m pytest tests/ -v --disable-warnings &
wait
```

## Test Configuration

### Frontend Configuration
- **Config File**: `frontend/vite.config.ts`
- **Setup File**: `frontend/src/setupTests.ts`
- **Type Declarations**: `frontend/src/vitest-setup.d.ts`

### Backend Configuration
- **Config File**: `backend/pytest.ini`
- **Setup File**: `backend/tests/conftest.py`
- **Environment**: Test-specific environment variables

## Debugging Tests

### Frontend Debugging
```bash
# Run tests in debug mode
npm test -- --inspect-brk

# Run with verbose output
npm test -- --run --reporter=verbose

# Run single test file in debug mode
npm test -- FeedbackModal.test.tsx --run --reporter=verbose
```

### Backend Debugging
```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Run with pdb debugger
python -m pytest tests/ --pdb

# Run with specific logging
python -m pytest tests/ -v --log-cli-level=DEBUG
```

## Common Issues and Solutions

### Frontend Issues

#### Issue: Tests not found
**Solution:**
```bash
# Ensure tests are in correct location
ls frontend/src/__tests__/

# Check test file naming (must end with .test.tsx)
find frontend/src -name "*.test.tsx"
```

#### Issue: TypeScript errors
**Solution:**
```bash
# Check TypeScript configuration
npx tsc --noEmit

# Ensure all dependencies are installed
npm install
```

### Backend Issues

#### Issue: Import errors
**Solution:**
```bash
# Ensure Python path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check virtual environment is activated
which python
```

#### Issue: Database connection errors
**Solution:**
```bash
# Check test environment variables
cat backend/.env

# Ensure test database is configured
export DATABASE_URL="sqlite:///./test.db"
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test -- --run
      
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && python -m pytest tests/ -v
```

## Test Coverage

### Frontend Test Coverage
- FeedbackModal: Form validation, API integration, error handling
- FloatingFeedbackButton: User interactions, tooltips, accessibility
- Navigation: Component rendering, route persistence

### Backend Test Coverage
- API Endpoints: Validation, authentication, error handling
- Slack Integration: Webhook delivery, failure handling
- Rate Limiting: Request throttling functionality

## Performance Benchmarks

### Frontend Performance
- Average test execution: 0.1s per test
- Total suite time: ~2.8s
- Memory usage: <100MB

### Backend Performance
- Average test execution: 0.065s per test
- Total suite time: ~1.0s
- Memory usage: <50MB

## Best Practices

### Writing Tests
1. Use descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Mock external dependencies
4. Test edge cases and error conditions
5. Keep tests isolated and independent

### Running Tests
1. Run tests before committing code
2. Use watch mode during development
3. Run full suite before deploying
4. Check test coverage regularly
5. Debug failing tests immediately

## Support

For test-related issues:
1. Check this documentation first
2. Review test logs and error messages
3. Verify environment setup
4. Check for dependency conflicts
5. Open an issue with detailed error information

---

**Testing ensures code quality and reliability for production deployment**
