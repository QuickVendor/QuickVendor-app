import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from io import BytesIO

from app.core.database import get_db
from app.core.sentry import add_breadcrumb, capture_message_with_context, capture_custom_error
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest, ProductResponse, ClickTrackingResponse, ErrorResponse
from app.api.deps import get_current_user
from app.services.s3_manager import get_s3_manager

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_uploaded_file(file: UploadFile, product_id: str) -> str:
    """Save uploaded file and return URL path"""
    if file and file.filename:
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Generate filename with product ID to avoid conflicts
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{product_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Construct full URL for production or relative path for development
        from app.core.config import settings
        if settings.BASE_URL:
            return f"{settings.BASE_URL}/uploads/{filename}"
        else:
            return f"/uploads/{filename}"
    return None


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"}
    }
)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    image_4: Optional[UploadFile] = File(None),
    image_5: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product for the authenticated user.
    
    - **name**: Product name (required)
    - **price**: Product price (required, must be > 0)
    - **description**: Product description (optional)
    - **is_available**: Product availability status (default: True)
    - **image_1**: First product image file (optional)
    - **image_2**: Second product image file (optional)
    - **image_3**: Third product image file (optional)
    - **image_4**: Fourth product image file (optional)
    - **image_5**: Fifth product image file (optional)
    """
    # Add breadcrumb for product creation attempt
    add_breadcrumb(
        message=f"Product creation attempt: {name}",
        category="product",
        level="info",
        data={
            "product_name": name,
            "price": price,
            "user_id": str(current_user.id),
            "has_images": any(img and img.filename for img in [image_1, image_2, image_3, image_4, image_5])
        }
    )
    
    # Validate price
    if price <= 0:
        logging.warning(f"Invalid price validation failed for user {current_user.id}: {price}")
        add_breadcrumb(
            message="Product creation failed - invalid price",
            category="product",
            level="warning",
            data={"price": price, "user_id": str(current_user.id)}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )
    
    # Create product
    new_product = Product(
        name=name,
        description=description,
        price=price,
        is_available=is_available,
        user_id=current_user.id
    )
    
    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Handle multiple image uploads
        images = [image_1, image_2, image_3, image_4, image_5]
        for i, image in enumerate(images, 1):
            if image and image.filename:
                image_url = await save_uploaded_file(image, f"{new_product.id}_img{i}")
                setattr(new_product, f'image_url_{i}', image_url)
        
        if any(image and image.filename for image in images):
            db.commit()
            db.refresh(new_product)
        
        # Log successful product creation
        logging.info(f"Product created successfully: {new_product.id} by user {current_user.id}")
        add_breadcrumb(
            message="Product creation successful",
            category="product",
            level="info",
            data={
                "product_id": str(new_product.id),
                "product_name": new_product.name,
                "user_id": str(current_user.id)
            }
        )
        
        # Capture success message
        capture_message_with_context(
            "New product created",
            level="info",
            context={
                "product_id": str(new_product.id),
                "product_name": new_product.name,
                "user_id": str(current_user.id),
                "price": new_product.price
            }
        )
        
        return ProductResponse.from_db_model(new_product)
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create product for user {current_user.id}: {str(e)}")
        
        # Capture error with context
        capture_custom_error(e, {
            "operation": "create_product",
            "user_id": str(current_user.id),
            "product_name": name,
            "price": price
        })
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create product"
        )


@router.get(
    "/",
    response_model=List[ProductResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"}
    }
)
async def get_my_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all products owned by the authenticated user.
    
    Returns a list of all products created by the current user.
    """
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    return [ProductResponse.from_db_model(product) for product in products]


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Product not found"}
    }
)
async def update_product(
    product_id: str,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image_1: Optional[UploadFile] = File(None),
    image_2: Optional[UploadFile] = File(None),
    image_3: Optional[UploadFile] = File(None),
    image_4: Optional[UploadFile] = File(None),
    image_5: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing product owned by the authenticated user.
    
    - **product_id**: ID of the product to update
    - **name**: Updated product name (optional)
    - **price**: Updated product price (optional, must be > 0)
    - **description**: Updated product description (optional)
    - **is_available**: Updated product availability status (optional)
    - **image_1**: First product image file (optional)
    - **image_2**: Second product image file (optional)
    - **image_3**: Third product image file (optional)
    - **image_4**: Fourth product image file (optional)
    - **image_5**: Fifth product image file (optional)
    """
    # Find the product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Validate price if provided
    if price is not None and price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )
    
    # Update fields if provided
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if is_available is not None:
        product.is_available = is_available
    
    # Handle multiple image uploads
    images = [image_1, image_2, image_3, image_4, image_5]
    for i, image in enumerate(images, 1):
        if image and image.filename:
            # Delete old image if exists
            old_image_url = getattr(product, f'image_url_{i}', None)
            if old_image_url and os.path.exists(old_image_url.lstrip('/')):
                os.remove(old_image_url.lstrip('/'))
            
            # Save new image
            image_url = await save_uploaded_file(image, f"{product.id}_img{i}")
            setattr(product, f'image_url_{i}', image_url)
    
    try:
        db.commit()
        db.refresh(product)
        return ProductResponse.from_db_model(product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product"
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Product not found"}
    }
)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a product owned by the authenticated user.
    
    - **product_id**: ID of the product to delete
    """
    # Find the product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        # Delete associated image files if they exist
        for i in range(1, 6):  # image_url_1 through image_url_5
            image_url = getattr(product, f'image_url_{i}', None)
            if image_url:
                # Handle both relative and absolute URLs
                file_path = image_url.lstrip('/') if image_url.startswith('/') else image_url
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        db.delete(product)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete product: {str(e)}"
        )


@router.post(
    "/{product_id}/track-click",
    response_model=ClickTrackingResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Product not found"}
    }
)
async def track_product_click(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Track a click on a product by incrementing its click counter.
    
    This is a public endpoint that can be used to track customer interest
    in products without requiring authentication.
    
    - **product_id**: ID of the product to track click for
    """
    # Find the product
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        # Increment click count
        product.click_count += 1
        db.commit()
        
        return ClickTrackingResponse(message="Click tracked successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to track click"
        )


# ========================= S3 Image Upload Endpoints =========================

@router.post(
    "/{product_id}/images/upload",
    response_model=Dict[str, Any],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or upload error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "S3 service error"}
    }
)
async def upload_product_image_to_s3(
    product_id: str,
    image: UploadFile = File(..., description="Product image file to upload"),
    image_slot: int = Form(1, ge=1, le=5, description="Image slot number (1-5)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a product image to AWS S3.
    
    This endpoint uploads product images directly to S3 and returns the public URL.
    Images are stored in a structured format: product-images/{product_id}/{unique_filename}
    
    - **product_id**: ID of the product to upload image for
    - **image**: Image file to upload (JPEG, PNG, GIF, WebP, BMP)
    - **image_slot**: Image slot number (1-5) to store the image URL in
    
    Returns:
    - **url**: Public S3 URL of the uploaded image
    - **key**: S3 object key
    - **filename**: Generated unique filename
    - **product_id**: Product ID
    - **image_slot**: Image slot number used
    """
    # Add breadcrumb for S3 upload attempt
    add_breadcrumb(
        message=f"S3 image upload attempt for product {product_id}",
        category="s3_upload",
        level="info",
        data={
            "product_id": product_id,
            "user_id": str(current_user.id),
            "filename": image.filename,
            "content_type": image.content_type,
            "image_slot": image_slot
        }
    )
    
    # Verify product ownership
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        logging.warning(f"Product not found or unauthorized: {product_id} for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission to modify it"
        )
    
    # Check file size (limit to 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    file_content = await image.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        logging.warning(f"File size exceeded for product {product_id}: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of 10MB. Your file: {file_size / (1024*1024):.2f}MB"
        )
    
    # Reset file pointer for S3 upload
    file_like = BytesIO(file_content)
    
    try:
        # Initialize S3 manager
        s3_manager = get_s3_manager()
        
        # Check if S3 is configured, if not fallback to local storage
        if not s3_manager.is_s3_configured():
            logging.warning(f"S3 not configured, falling back to local storage for product {product_id}")
            
            # Reset file pointer for local storage
            image.file.seek(0)
            
            # Save to local storage using existing function
            image_url = await save_uploaded_file(image, f"{product_id}_img{image_slot}")
            
            if not image_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save image to local storage."
                )
            
            # Update product with local image URL
            image_field = f"image_url_{image_slot}"
            setattr(product, image_field, image_url)
            db.commit()
            db.refresh(product)
            
            logging.info(f"Successfully uploaded image to local storage for product {product_id}, slot {image_slot}")
            
            return {
                "url": image_url,
                "filename": image.filename,
                "product_id": product_id,
                "image_slot": image_slot,
                "storage_type": "local"
            }
        
        # Upload to S3
        upload_result = await s3_manager.upload_product_image(
            file_content=file_like,
            filename=image.filename,
            product_id=product_id,
            content_type=image.content_type
        )
        
        # Update product with new image URL
        image_field = f"image_url_{image_slot}"
        
        # Delete old S3 image if exists (optional - uncomment if you want to clean up old images)
        # old_url = getattr(product, image_field, None)
        # if old_url and old_url.startswith("https://") and ".s3." in old_url:
        #     # Extract S3 key from URL and delete
        #     old_key = old_url.split(".amazonaws.com/")[-1]
        #     await s3_manager.delete_product_image(old_key)
        
        # Update product with new S3 URL
        setattr(product, image_field, upload_result["url"])
        db.commit()
        db.refresh(product)
        
        # Log successful upload
        logging.info(f"Successfully uploaded image to S3 for product {product_id}, slot {image_slot}")
        add_breadcrumb(
            message="S3 image upload successful",
            category="s3_upload",
            level="info",
            data={
                "product_id": product_id,
                "s3_key": upload_result["key"],
                "image_slot": image_slot
            }
        )
        
        # Capture success message
        capture_message_with_context(
            "Product image uploaded to S3",
            level="info",
            context={
                "product_id": product_id,
                "user_id": str(current_user.id),
                "s3_url": upload_result["url"],
                "image_slot": image_slot
            }
        )
        
        # Add image_slot to response
        upload_result["image_slot"] = image_slot
        upload_result["storage_type"] = "s3"
        
        return upload_result
        
    except ValueError as e:
        # S3Manager not initialized (missing credentials)
        logging.error(f"S3Manager initialization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 service is not configured. Please contact support."
        )
    except HTTPException:
        # Re-raise HTTPExceptions from S3Manager
        raise
    except Exception as e:
        # Unexpected error
        logging.error(f"Unexpected error during S3 upload for product {product_id}: {str(e)}")
        capture_custom_error(e, {
            "operation": "upload_product_image_to_s3",
            "product_id": product_id,
            "user_id": str(current_user.id),
            "filename": image.filename,
            "image_slot": image_slot
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image. Please try again later."
        )


@router.delete(
    "/{product_id}/images/{image_slot}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Product or image not found"},
        500: {"model": ErrorResponse, "description": "S3 service error"}
    }
)
async def delete_product_image_from_s3(
    product_id: str,
    image_slot: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a product image from AWS S3.
    
    This endpoint deletes a specific product image from S3 and removes the URL from the database.
    
    - **product_id**: ID of the product
    - **image_slot**: Image slot number (1-5) to delete
    """
    # Validate image slot
    if image_slot < 1 or image_slot > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image slot must be between 1 and 5"
        )
    
    # Verify product ownership
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission to modify it"
        )
    
    # Get the image URL
    image_field = f"image_url_{image_slot}"
    image_url = getattr(product, image_field, None)
    
    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image found in slot {image_slot}"
        )
    
    # Check if it's an S3 URL
    if image_url.startswith("https://") and ".s3." in image_url:
        try:
            # Extract S3 key from URL
            s3_key = image_url.split(".amazonaws.com/")[-1]
            
            # Initialize S3 manager and delete from S3
            s3_manager = get_s3_manager()
            await s3_manager.delete_product_image(s3_key)
            
            logging.info(f"Deleted S3 image for product {product_id}, slot {image_slot}")
        except Exception as e:
            logging.error(f"Error deleting S3 image: {str(e)}")
            # Continue to remove from database even if S3 deletion fails
    
    # Remove URL from database
    setattr(product, image_field, None)
    db.commit()
    
    return None


@router.get(
    "/s3/status",
    response_model=Dict[str, Any],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        503: {"model": ErrorResponse, "description": "S3 service unavailable"}
    }
)
async def check_s3_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check S3 service status and configuration.
    
    This endpoint validates that S3 is properly configured and accessible.
    Useful for debugging and monitoring.
    
    Returns:
    - **status**: "connected" or "error"
    - **bucket_configured**: Whether S3 bucket is configured
    - **message**: Status message
    """
    try:
        s3_manager = get_s3_manager()
        
        if not s3_manager.is_s3_configured():
            return {
                "status": "not_configured",
                "bucket_configured": bool(os.getenv('S3_BUCKET_NAME')),
                "message": "S3 service is not configured. Using local storage as fallback.",
                "storage_type": "local"
            }
        
        is_connected = await s3_manager.validate_s3_connection()
        
        if is_connected:
            return {
                "status": "connected",
                "bucket_configured": True,
                "message": "S3 service is properly configured and accessible",
                "bucket_name": os.getenv('S3_BUCKET_NAME', 'Not configured'),
                "region": os.getenv('AWS_REGION', 'Not configured'),
                "storage_type": "s3"
            }
        else:
            return {
                "status": "error",
                "bucket_configured": bool(os.getenv('S3_BUCKET_NAME')),
                "message": "S3 service is configured but not accessible. Check permissions.",
                "storage_type": "local"
            }
    except Exception as e:
        logging.error(f"Error checking S3 status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to check S3 service status"
        )
