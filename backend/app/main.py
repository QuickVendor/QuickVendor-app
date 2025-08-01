from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.database import engine, Base
from app.api import users, auth, products, store

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="QuickVendor API",
    description="Backend API for QuickVendor application",
    version="1.0.0"
)

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
    "https://quickvendor-app.onrender.com"
])

# In production, also allow the specific domain patterns
if os.getenv("ENVIRONMENT") == "production":
    # Allow all HTTPS origins ending with .onrender.com
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.onrender\.com",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Development CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
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
