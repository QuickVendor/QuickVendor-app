from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import logging

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.sentry import set_user_context, add_breadcrumb, capture_message_with_context
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
    # Add breadcrumb for login attempt
    add_breadcrumb(
        message=f"Login attempt for email: {login_data.email}",
        category="auth",
        level="info",
        data={"email": login_data.email}
    )
    
    # Check for existing user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Log failed login attempt
        logging.warning(f"Failed login attempt for email: {login_data.email}")
        add_breadcrumb(
            message="Login failed - invalid credentials",
            category="auth",
            level="warning",
            data={"email": login_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set user context in Sentry
    set_user_context(user_id=str(user.id), email=user.email)
    
    # Log successful login
    logging.info(f"Successful login for user: {user.email}")
    add_breadcrumb(
        message="User login successful",
        category="auth",
        level="info",
        data={"user_id": str(user.id), "email": user.email}
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
    # Add logout breadcrumb
    add_breadcrumb(
        message="User logout initiated",
        category="auth",
        level="info"
    )
    
    is_production = os.getenv("RENDER") is not None or os.getenv("ENVIRONMENT") == "production"
    
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=is_production,
        httponly=True,
        samesite="none" if is_production else "lax",
        domain=None
    )
    
    # Log successful logout
    logging.info("User logged out successfully")
    
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


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh an expired token with a new one."""
    try:
        # Try to get token from request (cookie or header)
        token = None
        
        # Check Authorization header first
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
        
        # Check cookie if no header
        if not token:
            token = request.cookies.get("access_token")
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token provided"
            )
        
        # Decode token without verification to get the email
        from jose import jwt
        try:
            # Decode without verification to get payload even if expired
            unverified_payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration
            )
            email = unverified_payload.get("sub")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Verify user exists
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Create new token
            new_access_token = create_access_token(
                data={"sub": user.email}
            )
            
            # Set new cookie
            is_production = os.getenv("RENDER") is not None or os.getenv("ENVIRONMENT") == "production"
            
            if is_production:
                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    secure=True,
                    samesite="none",
                    max_age=60*60*24*7,  # 7 days
                    path="/",
                    domain=None
                )
            else:
                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    secure=False,
                    samesite="lax",
                    max_age=60*60*24*7,  # 7 days
                    path="/",
                    domain=None
                )
            
            logging.info(f"Token refreshed for user: {user.email}")
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "message": "Token refreshed successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


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
        return {"authenticated": False, "source": "expired", "error": str(e)}
    except Exception as e:
        print(f"DEBUG check-session: Unexpected error - {e}")
        return {"authenticated": False, "source": "error"}
