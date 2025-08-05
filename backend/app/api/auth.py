from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    # Check for existing user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    # Set secure HTTP-only cookie with environment-aware settings
    is_production = os.getenv("RENDER") is not None or os.getenv("ENVIRONMENT") == "production"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,  # Only require HTTPS in production
        samesite="lax",  # Use lax for better cross-site compatibility
        max_age=60*60*24*7,  # 7 days
        path="/",
        domain=None  # Let browser handle domain automatically
    )
    
    # Also include token in response body for debugging/fallback
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "debug_info": {
            "cookie_set": True,
            "production": is_production,
            "secure": is_production
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing the authentication cookie.
    """
    is_production = os.getenv("RENDER") is not None or os.getenv("ENVIRONMENT") == "production"
    
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=is_production,
        httponly=True,
        samesite="none" if is_production else "lax",
        domain=None
    )
    return {"message": "Successfully logged out"}


@router.get("/debug")
async def debug_auth(request: Request):
    """Debug endpoint to check cookie and header values."""
    cookies = dict(request.cookies)
    headers = dict(request.headers)
    
    return {
        "cookies": cookies,
        "headers": {k: v for k, v in headers.items() if k.lower() in ['authorization', 'cookie', 'origin', 'user-agent']},
        "access_token_cookie": request.cookies.get("access_token"),
        "authorization_header": headers.get("authorization")
    }
