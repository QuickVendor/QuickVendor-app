import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.sentry import add_breadcrumb, capture_message_with_context, capture_custom_error
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest, ProductResponse, ClickTrackingResponse, ErrorResponse
from app.api.deps import get_current_user

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_uploaded_file(file: UploadFile, product_id: str) -> str:
    """Save uploaded file and return the file path."""
    if file.filename:
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{product_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return path relative to the server root for proper URL construction
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
        # Delete associated image file if exists
        if product.image_url and os.path.exists(product.image_url.lstrip('/')):
            os.remove(product.image_url.lstrip('/'))
        
        db.delete(product)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete product"
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
