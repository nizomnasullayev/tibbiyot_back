from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schema.order_schema import OrderCreate, OrderStatusUpdate, OrderOut, OrderListOut
from app.service.order_service import OrderService
from app.depedencies.auth import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order for the authenticated user
    """
    return OrderService.create_order(db, order, current_user.id)


@router.get("/my", response_model=List[OrderListOut])
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for the authenticated user
    """
    return OrderService.get_user_orders(db, current_user.id, skip, limit)


@router.get("/{order_id}", response_model=OrderOut)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific order
    """
    return OrderService.get_order_by_id(db, order_id, current_user.id)


@router.patch("/{order_id}/status", response_model=OrderOut)
def change_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change order status
    Valid statuses: pending, completed, delivered, cancelled
    """
    return OrderService.update_order_status(db, order_id, status_update, current_user.id)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order (only allowed within 5 minutes of creation)
    """
    return OrderService.cancel_order(db, order_id, current_user.id)