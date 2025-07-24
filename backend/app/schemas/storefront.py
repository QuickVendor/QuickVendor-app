from pydantic import BaseModel
from typing import List


class PublicProductResponse(BaseModel):
    id: str
    name: str
    price: float
    image_url: str | None = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "product_uuid_1",
                "name": "Cool T-Shirt",
                "price": 5000,
                "image_url": "/path/to/image.jpg"
            }
        }


class StorefrontResponse(BaseModel):
    vendor_name: str
    whatsapp_number: str
    products: List[PublicProductResponse]

    class Config:
        schema_extra = {
            "example": {
                "vendor_name": "Awesome Wears",
                "whatsapp_number": "2348012345678",
                "products": [
                    {
                        "id": "product_uuid_1",
                        "name": "Cool T-Shirt",
                        "price": 5000,
                        "image_url": "/path/to/image.jpg"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    detail: str
