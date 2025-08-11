from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    is_available: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Premium Coffee Beans",
                "description": "High-quality arabica coffee beans from Ethiopia",
                "price": 25.99,
                "is_available": True
            }
        }
    }


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Product Name",
                "description": "Updated description",
                "price": 29.99,
                "is_available": True
            }
        }
    }


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    image_urls: List[str] = []
    is_available: bool
    click_count: int
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_db_model(cls, product):
        """Convert database model to response model with image_urls list"""
        image_urls = []
        for i in range(1, 6):  # Check image_url_1 through image_url_5
            image_url = getattr(product, f'image_url_{i}', None)
            if image_url:
                image_urls.append(image_url)
        
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            image_urls=image_urls,
            is_available=product.is_available,
            click_count=product.click_count,
            user_id=product.user_id,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        json_schema_extra = {
            "example": {
                "id": "product_abc123",
                "name": "Premium Coffee Beans",
                "description": "High-quality arabica coffee beans from Ethiopia",
                "price": 25.99,
                "image_url": "/uploads/product_abc123.jpg",
                "is_available": True,
                "click_count": 42,
                "user_id": "user_xyz789",
                "created_at": "2025-07-24T10:30:00Z",
                "updated_at": "2025-07-24T10:30:00Z"
            }
        }


class ClickTrackingResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Click tracked successfully"
            }
        }


class ErrorResponse(BaseModel):
    detail: str
