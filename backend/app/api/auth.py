from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

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
    
    # Set secure HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Only send over HTTPS in production
        samesite="lax",  # Provides CSRF protection while allowing some cross-site usage
        max_age=60*60*24*7,  # 7 days
        path="/"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing the authentication cookie.
    """
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}
