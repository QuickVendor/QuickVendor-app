from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    is_available: bool = True

    class Config:
        schema_extra = {
            "example": {
                "name": "Premium Coffee Beans",
                "description": "High-quality arabica coffee beans from Ethiopia",
                "price": 25.99,
                "is_available": True
            }
        }


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Product Name",
                "description": "Updated description",
                "price": 29.99,
                "is_available": True
            }
        }


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None
    is_available: bool
    click_count: int
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
        schema_extra = {
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
        schema_extra = {
            "example": {
                "message": "Click tracked successfully"
            }
        }


class ErrorResponse(BaseModel):
    detail: str
