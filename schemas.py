
from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    compare_at_price: Optional[float] = None
    cost_per_item: Optional[float] = None
    profit: Optional[float] = None
    margin: Optional[float] = None
    track_quantity: Optional[bool] = None
    status: Optional[str] = None
    sales_channels: Optional[str] = None
    markets: Optional[str] = None
    product_type: Optional[str] = None
    vendor: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    collections: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None  # Make category optional


class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
  id: int

class Config:
     from_attributes = True  # Make sure you're using from_attributes instead of orm_mode