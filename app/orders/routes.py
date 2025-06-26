from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.models import Order, OrderItem, CartItem, Product, User
from .schemas import OrderResponse, OrderHistoryResponse, OrderItemResponse

router = APIRouter()

@router.post("/checkout", response_model=dict)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = 0
    order_items = []
    
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.name}"
            )
        
        total_amount += product.price * item.quantity
        order_items.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "price_at_purchase": product.price
        })
    
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="paid"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price_at_purchase=item["price_at_purchase"]
        )
        db.add(order_item)
        
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if product:
            product.stock -= item["quantity"]
    
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Checkout successful", "order_id": new_order.id}

@router.get("/orders", response_model=List[OrderHistoryResponse])
def get_order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    order_details = OrderResponse(
        id=order.id,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        items=[]
    )
    
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue  # skip to next item if product not found
        order_details.items.append(OrderItemResponse(
            product_id=item.product_id,
            name=product.name,
            quantity=item.quantity,
            price=item.price_at_purchase,
            subtotal=item.price_at_purchase * item.quantity,
            image_url=product.image_url
        ))
    
    return order_details