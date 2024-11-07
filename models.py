from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from database import Base


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
    price = Column(Float)
    compare_at_price = Column(Float)
    cost_per_item = Column(Float)
    profit = Column(Float, default=0.0)
    margin = Column(Float, default=0.0)
    quantity = Column(Integer, default=0)
    category = Column(String)
    vendor = Column(String)
    sku = Column(String)
    barcode = Column(String)
    tags = Column(String)
    image_url = Column(String, nullable=True)  # New field to store image UR