from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.sentry import add_breadcrumb, capture_message_with_context
from app.models.user import User
from app.models.product import Product
from app.schemas.storefront import StorefrontResponse, PublicProductResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/{store_identifier}",
    response_model=StorefrontResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Store not found"}
    }
)
async def get_public_storefront(
    store_identifier: str,
    db: Session = Depends(get_db)
):
    """
    Get public storefront data for a given store.
    
    This is a public endpoint that displays all available (in-stock) products
    for a specific vendor's storefront.
    
    - **store_identifier**: The store's custom slug OR username (extracted from email before @)
    
    Returns vendor information and all available products.
    """
    # Add breadcrumb for storefront access
    add_breadcrumb(
        message=f"Storefront access attempt for: {store_identifier}",
        category="storefront",
        level="info",
        data={"store_identifier": store_identifier}
    )
    
    # First try to find by store_slug (custom URL)
    user = db.query(User).filter(
        User.store_slug == store_identifier
    ).first()
    
    # If not found, try to find by username (email prefix) for backward compatibility
    if not user:
        user = db.query(User).filter(
            User.email.like(f"{store_identifier}@%")
        ).first()
    
    if not user:
        logging.warning(f"Storefront not found for: {store_identifier}")
        add_breadcrumb(
            message="Storefront not found",
            category="storefront",
            level="warning",
            data={"store_identifier": store_identifier}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Get all available (in-stock) products for this user
    available_products = db.query(Product).filter(
        Product.user_id == user.id,
        Product.is_available == True
    ).all()
    
    # Convert products to public response format
    public_products = []
    for product in available_products:
        # Collect all image URLs
        image_urls = []
        for i in range(1, 6):
            image_url = getattr(product, f'image_url_{i}', None)
            if image_url:
                image_urls.append(image_url)
        
        public_products.append(PublicProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            image_urls=image_urls,
            description=product.description,
            is_available=product.is_available
        ))
    
    # Use custom store name if available, otherwise extract from email
    if user.store_name:
        vendor_name = user.store_name
    else:
        vendor_name = user.email.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
    
    # Log successful storefront access
    logging.info(f"Storefront accessed successfully for user: {user.email} ({len(public_products)} products)")
    add_breadcrumb(
        message="Storefront access successful",
        category="storefront",
        level="info",
        data={
            "store_identifier": store_identifier,
            "vendor_email": user.email,
            "product_count": len(public_products)
        }
    )
    
    # Capture storefront view event
    capture_message_with_context(
        "Storefront viewed",
        level="info",
        context={
            "store_identifier": store_identifier,
            "vendor_id": str(user.id),
            "vendor_email": user.email,
            "product_count": len(public_products)
        }
    )
    
    return StorefrontResponse(
        vendor_name=vendor_name,
        whatsapp_number=user.whatsapp_number,
        products=public_products,
        banner_url=user.banner_url,
        store_slug=user.store_slug
    )
