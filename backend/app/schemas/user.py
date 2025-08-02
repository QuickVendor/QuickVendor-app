from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    whatsapp_number: str = Field(..., pattern="^[0-9]{10,15}$")

    class Config:
        schema_extra = {
            "example": {
                "email": "vendor@example.com",
                "password": "strongpassword123",
                "whatsapp_number": "2348012345678"
            }
        }


class UserRegisterResponse(BaseModel):
    id: str
    email: str

    class Config:
        schema_extra = {
            "example": {
                "id": "user_uuid",
                "email": "vendor@example.com"
            }
        }


class ErrorResponse(BaseModel):
    detail: str


class UserProfile(BaseModel):
    id: str
    email: str
    whatsapp_number: str
    store_url: str | None = None

    class Config:
        from_attributes = True
