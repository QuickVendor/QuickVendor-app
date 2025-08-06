from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.sentry import set_user_context, add_breadcrumb, capture_message_with_context
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserRegisterResponse, ErrorResponse, UserProfile
from app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "Email already exists"}
    }
)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new vendor account.
    
    - **email**: Vendor's email address (must be unique)
    - **password**: Strong password (minimum 8 characters)
    - **whatsapp_number**: WhatsApp contact number (10-15 digits)
    """
    # Add registration attempt breadcrumb
    add_breadcrumb(
        message=f"User registration attempt for email: {user_data.email}",
        category="user",
        level="info",
        data={"email": user_data.email}
    )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logging.warning(f"Registration attempt with existing email: {user_data.email}")
        add_breadcrumb(
            message="Registration failed - email already exists",
            category="user",
            level="warning",
            data={"email": user_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        whatsapp_number=user_data.whatsapp_number
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Set user context in Sentry
        set_user_context(user_id=str(new_user.id), email=new_user.email)
        
        # Log successful registration
        logging.info(f"New user registered successfully: {new_user.email}")
        add_breadcrumb(
            message="User registration successful",
            category="user",
            level="info",
            data={"user_id": str(new_user.id), "email": new_user.email}
        )
        
        # Capture success message
        capture_message_with_context(
            "New user registered",
            level="info",
            context={
                "user_id": str(new_user.id),
                "email": new_user.email,
                "registration_source": "api"
            }
        )
        
        return UserRegisterResponse(
            id=new_user.id,
            email=new_user.email
        )
    except IntegrityError:
        db.rollback()
        logging.error(f"Database integrity error during registration for: {user_data.email}")
        add_breadcrumb(
            message="Registration failed - database integrity error",
            category="user",
            level="error",
            data={"email": user_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Requires authentication via Bearer token.
    """
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        whatsapp_number=current_user.whatsapp_number,
        store_url=None  # Frontend will generate the correct URL
    )
