from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
    

from typing import Optional
from pydantic import BaseModel

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    compare_at_price: Optional[float] = None
    cost_per_item: Optional[float] = None
    quantity: int = 0
    category: Optional[str] = None
    vendor: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None  # URL to the product image

class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True  # Make sure you're using from_attributes instead of orm_mode
