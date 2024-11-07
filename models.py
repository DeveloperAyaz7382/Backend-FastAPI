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

class ProductDB(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)
    cost_per_item = Column(Float, nullable=True)
    quantity = Column(Integer, default=0)
    category = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    barcode = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    image_url = Column(String, nullable=True)