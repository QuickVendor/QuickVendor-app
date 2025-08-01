from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.storefront import StorefrontResponse, PublicProductResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/{username}",
    response_model=StorefrontResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Username not found"}
    }
)
async def get_public_storefront(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get public storefront data for a given username.
    
    This is a public endpoint that displays all available (in-stock) products
    for a specific vendor's storefront.
    
    - **username**: The vendor's username (extracted from email before @)
    
    Returns vendor information and all available products.
    """
    # Find user by extracting username from email
    # Username is the part before @ in the email
    user = db.query(User).filter(
        User.email.like(f"{username}@%")
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found"
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
    
    # Extract vendor name from email (part before @)
    vendor_name = user.email.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
    
    return StorefrontResponse(
        vendor_name=vendor_name,
        whatsapp_number=user.whatsapp_number,
        products=public_products
    )
