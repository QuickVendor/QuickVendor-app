from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_password_hash
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
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
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
        
        return UserRegisterResponse(
            id=new_user.id,
            email=new_user.email
        )
    except IntegrityError:
        db.rollback()
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
