from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.api import users, auth

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

# Root endpoint
@app.get("/")
async def root():
    return {"message": "QuickVendor API is running"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "QuickVendor API is healthy"}
