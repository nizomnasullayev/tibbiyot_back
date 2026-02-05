from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.models.order import Order
from app.models.order_product import OrderProduct
from app.models.product import Product
from app.schema.order_schema import OrderCreate, OrderStatusUpdate, OrderOut, OrderListOut


class OrderService:
    """Service layer for order operations"""

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate, user_id: UUID) -> Order:
        """
        Create a new order with products
        """
        try:
            # Validate and fetch products
            order_products = []
            total_price = Decimal('0.00')

            for item in order_data.products:
                # Fetch product from database
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product with id {item.product_id} not found"
                    )

                item_price = Decimal(str(product.price))
                item_total = item_price * item.quantity
                total_price += item_total

                order_product = OrderProduct(
                    product_id=product.id,
                    price=item_price,
                    quantity=item.quantity,
                    total_price=item_total,
                    name=product.name,
                    image=getattr(product, 'image', None),
                    weight=getattr(product, 'weight', None),
                    rating=getattr(product, 'rating', None),
                    description=getattr(product, 'description', None),
                )
                order_products.append(order_product)

            # Create order
            new_order = Order(
                user_id=user_id,
                total_price=total_price,
                payment_method=order_data.payment_method,
                shipping_address=order_data.shipping_address,
                phone=order_data.phone,
                notes=order_data.notes,
                delivery_date=order_data.delivery_date,
                location=order_data.location,
                status="pending"
            )

            # Add products to order
            new_order.products = order_products

            db.add(new_order)
            db.commit()
            db.refresh(new_order)

            return new_order

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating order: {str(e)}"
            )

    @staticmethod
    def get_user_orders(
            db: Session,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a specific user
        """
        orders = db.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

        return orders

    @staticmethod
    def get_order_by_id(db: Session, order_id: int, user_id: UUID) -> Order:
        """
        Get order by ID with products loaded
        User can only access their own orders
        """
        order = db.query(Order).options(
            joinedload(Order.products)
        ).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        return order

    @staticmethod
    def update_order_status(
            db: Session,
            order_id: int,
            status_data: OrderStatusUpdate,
            user_id: UUID
    ) -> Order:
        """
        Update order status
        """
        try:
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.user_id == user_id
            ).first()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )

            # Validate status change
            valid_statuses = ["pending", "completed", "delivered", "cancelled"]
            new_status = status_data.status.lower()

            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )

            order.status = new_status
            db.commit()
            db.refresh(order)
            return order

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    @staticmethod
    def cancel_order(db: Session, order_id: int, user_id: UUID) -> Order:
        """
        Cancel an order (only allowed within 5 minutes of creation)
        """
        try:
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.user_id == user_id
            ).first()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )

            # Check if order is already cancelled or completed
            if order.status in ["cancelled", "completed", "delivered"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot cancel order with status: {order.status}"
                )

            # Check if 5 minutes have passed
            now = datetime.now(timezone.utc)
            created_at = order.created_at

            # Ensure created_at is timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            time_elapsed = now - created_at

            if time_elapsed > timedelta(minutes=5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order can only be cancelled within 5 minutes of creation"
                )

            order.status = "cancelled"
            db.commit()
            db.refresh(order)
            return order

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )