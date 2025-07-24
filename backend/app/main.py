from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
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
