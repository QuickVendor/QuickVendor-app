from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
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
    
    # For cross-origin debugging: Use permissive settings temporarily
    if is_production:
        # Production: secure cross-origin cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Required for samesite=none
            samesite="none",  # Allow cross-site cookies
            max_age=60*60*24*7,  # 7 days
            path="/",
            domain=None
        )
    else:
        # Development: permissive settings
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Allow HTTP in development
            samesite="lax",  # Lax for development
            max_age=60*60*24*7,  # 7 days
            path="/",
            domain=None
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


@router.get("/check-session")
async def check_session(request: Request):
    """Simple endpoint to check if user has valid authentication."""
    try:
        # Try to get token from request (cookie or header)
        token = None
        
        # Check Authorization header first
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            print(f"DEBUG check-session: Found token in header: {token[:20]}...")
        
        # Check cookie if no header
        if not token:
            token = request.cookies.get("access_token")
            if token:
                print(f"DEBUG check-session: Found token in cookie: {token[:20]}...")
        
        if not token:
            print("DEBUG check-session: No token found")
            return {"authenticated": False, "source": "none"}
        
        # Validate token
        from jose import jwt, JWTError
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            print("DEBUG check-session: Invalid token payload")
            return {"authenticated": False, "source": "invalid"}
        
        print(f"DEBUG check-session: Valid token for {email}")
        return {
            "authenticated": True, 
            "email": email,
            "source": "header" if auth_header else "cookie"
        }
        
    except JWTError as e:
        print(f"DEBUG check-session: JWT error - {e}")
        return {"authenticated": False, "source": "expired"}
    except Exception as e:
        print(f"DEBUG check-session: Unexpected error - {e}")
        return {"authenticated": False, "source": "error"}
