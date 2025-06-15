from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .auth.routes import router as auth_router
from .products.routes import router as products_router
from .cart.routes import router as cart_router
from .orders.routes import router as orders_router
from .core.models import RoleEnum

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])

@app.get("/")
def read_root():
    return {"message": "E-commerce Backend API"}