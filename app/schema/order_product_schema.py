from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class OrderProductCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, default=1)


class OrderProductOut(BaseModel):
    id: int
    order_id: int
    product_id: str
    price: Decimal
    quantity: int
    total_price: Decimal
    name: str
    image: Optional[str] = None
    weight: Optional[str] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True