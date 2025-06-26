from pydantic import BaseModel

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float
    image_url: str

    class Config:
        from_attributes = True