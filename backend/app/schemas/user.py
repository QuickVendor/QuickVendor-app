from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    whatsapp_number: str = Field(..., pattern="^[0-9]{10,15}$")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "vendor@example.com",
                "password": "strongpassword123",
                "whatsapp_number": "2348012345678"
            }
        }
    }


class UserRegisterResponse(BaseModel):
    id: str
    email: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "user_uuid",
                "email": "vendor@example.com"
            }
        }
    }


class ErrorResponse(BaseModel):
    detail: str


class UserProfile(BaseModel):
    id: str
    email: str
    whatsapp_number: str
    store_url: str | None = None
    store_name: str | None = None
    store_slug: str | None = None
    banner_url: str | None = None

    model_config = {"from_attributes": True}


class UpdateStoreRequest(BaseModel):
    store_name: Optional[str] = Field(None, min_length=3, max_length=100)
    store_slug: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-z0-9-]+$")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "store_name": "John's Fashion Store",
                "store_slug": "johns-fashion"
            }
        }
    }
