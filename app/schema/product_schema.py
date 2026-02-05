from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    weight: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[int] = None
    weight: Optional[str] = None
    rating: Optional[int] = None


class ProductOut(ProductBase):
    id: str
    image: Optional[str] = None
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True



class ReviewOut(BaseModel):
    id: int
    title: str
    rating: int
    user_id: UUID
    product_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    title: str = Field(..., max_length=255)
    rating: int = Field(..., ge=1, le=5)