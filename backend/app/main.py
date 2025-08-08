from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.core.database import engine, Base
from app.core.sentry import init_sentry
from app.core.middleware import log_requests_middleware, SentryMiddleware
from app.api import users, auth, products, store, feedback

# Initialize Sentry before creating the app
init_sentry()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="QuickVendor API",
    description="Backend API for QuickVendor application",
    version="1.0.0"
)

# Add Sentry middleware first
app.add_middleware(SentryMiddleware)

# Add request logging middleware
app.middleware("http")(log_requests_middleware)

# Configure CORS - include production URLs
allowed_origins = [
    "http://localhost:5173", 
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://localhost:3000"
]

# Add production frontend URL if available
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

# Add common Render frontend patterns - allow all Render subdomains for flexibility
allowed_origins.extend([
    "https://*.onrender.com",
    "https://quickvendor-frontend.onrender.com",
    "https://quickvendor-app.onrender.com",
    "https://quick-vendor-app.onrender.com"  # Add the actual frontend URL
])

# Single CORS configuration - combining all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000",
        "https://quick-vendor-app.onrender.com",
        "https://quickvendor-app.onrender.com",
        "https://quickvendor-frontend.onrender.com"
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"]
)
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["authentication"]
)
app.include_router(
    products.router,
    prefix="/api/products",
    tags=["products"]
)
app.include_router(
    store.router,
    prefix="/api/store",
    tags=["storefront"]
)
app.include_router(
    feedback.router,
    prefix="/api/feedback",
    tags=["feedback"]
)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "QuickVendor API is running"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "QuickVendor API is healthy"}

# Sentry test endpoints (development only)
@app.get("/api/sentry/test-error")
async def test_sentry_error():
    """Test endpoint to verify Sentry error capture."""
    import os
    if os.getenv("ENVIRONMENT") == "production":
        return {"error": "Not available in production"}
    
    raise Exception("Test error for Sentry monitoring")

@app.get("/api/sentry/test-message")
async def test_sentry_message():
    """Test endpoint to verify Sentry message capture."""
    import os
    if os.getenv("ENVIRONMENT") == "production":
        return {"error": "Not available in production"}
    
    from app.core.sentry import capture_message_with_context
    
    message_id = capture_message_with_context(
        "Test message from QuickVendor API",
        level="info",
        context={"test_type": "message_capture", "endpoint": "/api/sentry/test-message"}
    )
    
    return {"message": "Test message sent to Sentry", "message_id": message_id}
