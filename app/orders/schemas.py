from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItemResponse(BaseModel):
    product_id: int
    name: str
    quantity: int
    price: float
    subtotal: float
    image_url: str

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True

class OrderHistoryResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True