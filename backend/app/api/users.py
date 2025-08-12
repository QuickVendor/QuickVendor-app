from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
import re
from io import BytesIO
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.sentry import set_user_context, add_breadcrumb, capture_message_with_context
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserRegisterResponse, ErrorResponse, UserProfile, UpdateStoreRequest
from app.api.deps import get_current_user
from app.services.s3_manager import get_s3_manager

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
        store_url=None,  # Frontend will generate the correct URL
        store_name=current_user.store_name,
        store_slug=current_user.store_slug,
        banner_url=current_user.banner_url
    )


@router.put("/me/store", response_model=UserProfile)
async def update_store_info(
    store_data: UpdateStoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update store information (name and slug).
    
    - **store_name**: Display name for the store (3-100 characters)
    - **store_slug**: URL-friendly identifier (3-50 characters, lowercase, numbers and hyphens only)
    
    The store_slug must be unique and will be used in the store URL.
    """
    try:
        # Update store name if provided
        if store_data.store_name is not None:
            current_user.store_name = store_data.store_name
        
        # Update and validate store slug if provided
        if store_data.store_slug is not None:
            # Check if slug is already taken by another user
            existing_slug = db.query(User).filter(
                User.store_slug == store_data.store_slug,
                User.id != current_user.id
            ).first()
            
            if existing_slug:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This store URL is already taken. Please choose another."
                )
            
            current_user.store_slug = store_data.store_slug
        
        db.commit()
        db.refresh(current_user)
        
        logging.info(f"Store info updated for user {current_user.email}: name={current_user.store_name}, slug={current_user.store_slug}")
        
        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            whatsapp_number=current_user.whatsapp_number,
            store_url=None,
            store_name=current_user.store_name,
            store_slug=current_user.store_slug,
            banner_url=current_user.banner_url
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This store URL is already taken."
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to update store info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update store information"
        )


@router.post("/me/banner", response_model=Dict[str, Any])
async def upload_store_banner(
    banner: UploadFile = File(..., description="Banner image file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a banner image for the store.
    
    - **banner**: Image file (JPEG, PNG, GIF, WebP, BMP)
    - Maximum file size: 5MB
    - Recommended dimensions: 1200x300 pixels
    
    The banner will be uploaded to S3 and the URL will be saved to the user's profile.
    """
    # Check file size (limit to 5MB for banners)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    file_content = await banner.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of 5MB. Your file: {file_size / (1024*1024):.2f}MB"
        )
    
    # Reset file pointer for S3 upload
    file_like = BytesIO(file_content)
    
    try:
        # Initialize S3 manager
        s3_manager = get_s3_manager()
        
        if not s3_manager.is_s3_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Image storage service is not available. Please try again later."
            )
        
        # Upload to S3 with a special path for banners
        upload_result = await s3_manager.upload_store_banner(
            file_content=file_like,
            filename=banner.filename,
            user_id=current_user.id,
            content_type=banner.content_type
        )
        
        # Delete old banner if exists
        if current_user.banner_url and current_user.banner_url.startswith("https://"):
            # Extract S3 key from URL and delete old banner
            try:
                old_key = current_user.banner_url.split(".amazonaws.com/")[-1]
                await s3_manager.delete_product_image(old_key)
            except:
                pass  # Ignore errors when deleting old banner
        
        # Update user with new banner URL
        current_user.banner_url = upload_result["url"]
        db.commit()
        db.refresh(current_user)
        
        logging.info(f"Banner uploaded successfully for user {current_user.email}")
        
        return {
            "message": "Banner uploaded successfully",
            "banner_url": upload_result["url"],
            "filename": upload_result["filename"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to upload banner: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload banner image. Please try again later."
        )


@router.delete("/me/banner", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store_banner(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the store banner image.
    """
    if not current_user.banner_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No banner image found"
        )
    
    try:
        # Delete from S3 if it's an S3 URL
        if current_user.banner_url.startswith("https://"):
            s3_manager = get_s3_manager()
            if s3_manager.is_s3_configured():
                try:
                    s3_key = current_user.banner_url.split(".amazonaws.com/")[-1]
                    await s3_manager.delete_product_image(s3_key)
                except:
                    pass  # Ignore S3 deletion errors
        
        # Clear banner URL from database
        current_user.banner_url = None
        db.commit()
        
        logging.info(f"Banner deleted for user {current_user.email}")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to delete banner: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete banner image"
        )
