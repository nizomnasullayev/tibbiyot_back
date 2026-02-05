from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.schema.order_product_schema import OrderProductCreate, OrderProductOut


class OrderCreate(BaseModel):
    payment_method: str = Field(min_length=1, max_length=50)
    shipping_address: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=255)
    delivery_date: Optional[datetime] = None
    location: Optional[dict] = None
    products: List[OrderProductCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=30)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ['pending', 'completed', 'delivered', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()


class OrderOut(BaseModel):
    id: int
    user_id: UUID
    total_price: int
    status: str
    payment_method: str
    shipping_address: str
    phone: str
    notes: Optional[str] = None
    created_at: datetime
    delivery_date: Optional[datetime] = None
    location: Optional[dict] = None
    products: List[OrderProductOut] = []

    class Config:
        from_attributes = True


class OrderListOut(BaseModel):
    """Simplified schema for listing orders"""
    id: int
    user_id: UUID
    total_price: Decimal
    status: str
    created_at: datetime
    delivery_date: Optional[datetime] = None

    class Config:
        from_attributes = True