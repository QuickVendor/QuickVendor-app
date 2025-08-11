from pydantic import BaseModel
from typing import List


class PublicProductResponse(BaseModel):
    id: str
    name: str
    price: float
    image_urls: List[str] = []
    description: str | None = None
    is_available: bool = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "product_uuid_1",
                "name": "Cool T-Shirt",
                "price": 5000,
                "image_urls": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
                "description": "Comfortable cotton t-shirt in various colors",
                "is_available": True
            }
        }


class StorefrontResponse(BaseModel):
    vendor_name: str
    whatsapp_number: str
    products: List[PublicProductResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "Awesome Wears",
                "whatsapp_number": "2348012345678",
                "products": [
                    {
                        "id": "product_uuid_1",
                        "name": "Cool T-Shirt",
                        "price": 5000,
                        "image_urls": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
                        "description": "Comfortable cotton t-shirt in various colors",
                        "is_available": True
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    detail: str
