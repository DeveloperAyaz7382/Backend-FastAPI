from sqlalchemy.ext.declarative import declarative_base
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, Float, Date


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    compare_at_price = Column(Float, nullable=True)
    cost_per_item = Column(Float)
    profit = Column(Float)
    margin = Column(Float)
    track_quantity = Column(Boolean)
    sku = Column(String)
    barcode = Column(String)
    status = Column(String)
    sales_channels = Column(String)
    markets = Column(String)
    product_type = Column(String)
    vendor = Column(String)
    collections = Column(String)
    tags = Column(String)
    image_url = Column(String, nullable=True)
  