# QuickVendor Setup Guide

## Prerequisites
- Python 3.8+ 
- Node.js 16+
- Git

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/QuickVendor/QuickVendor-app.git
cd QuickVendor-app
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env file with your configuration
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables  
cp .env.example .env
# Edit .env file with your configuration
```

### 4. Run Application

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

Visit: http://localhost:5173

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./quickvendor.db
SECRET_KEY=your-secret-key-here
SLACK_WEBHOOK_URL=your-slack-webhook-url
SENTRY_DSN=your-sentry-dsn-optional
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SENTRY_DSN=your-sentry-dsn-optional
VITE_NODE_ENV=development
```

## Documentation
Essential documentation is available in `/document_holder/`

## Support
Check the README.md for detailed information or refer to documentation in `/document_holder/`
