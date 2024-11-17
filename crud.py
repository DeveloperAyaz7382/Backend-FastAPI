# # crud.py
# from passlib.context import CryptContext
# from models import User
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# import models, schemas



# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def create_user(db: Session, name: str, email: str, password: str):
#     hashed_password = pwd_context.hash(password)
#     db_user = User(name=name, email=email, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def authenticate_user(db: Session, email: str, password: str):
#     user = db.query(User).filter(User.email == email).first()
#     if user and pwd_context.verify(password, user.hashed_password):
#         return user
#     return None





# def create_product(db: Session, product: schemas.ProductCreate):
#     db_product = models.ProductDB(**product.dict())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# def get_products(db: Session, skip: int = 0, limit: int = 10):
#     return db.query(models.ProductDB).offset(skip).limit(limit).all()

# def get_product(db: Session, product_id: int):
#     return db.query(models.ProductDB).filter(models.ProductDB.id == product_id).first()

# def update_product(db: Session, product_id: int, product: schemas.ProductCreate):
#     db_product = db.query(models.ProductDB).filter(models.ProductDB.id == product_id).first()
#     if not db_product:
#         return None
#     for key, value in product.dict(exclude_unset=True).items():
#         setattr(db_product, key, value)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# def delete_product(db: Session, product_id: int):
#     db_product = db.query(models.ProductDB).filter(models.ProductDB.id == product_id).first()
#     if not db_product:
#         return None
#     db.delete(db_product)
#     db.commit()
#     return db_product



# # def create_product(db: Session, product: schemas.ProductCreate):
# #     db_product = models.Product(**product.dict())
# #     db.add(db_product)
# #     db.commit()
# #     db.refresh(db_product)
# #     return db_product

# # def get_product(db: Session, product_id: int):
# #     return db.query(models.Product).filter(models.Product.id == product_id).first()

# # def get_products(db: Session, skip: int = 0, limit: int = 10):
# #     return db.query(models.Product).offset(skip).limit(limit).all()

# # def update_product(db: Session, product_id: int, product: schemas.ProductCreate):
# #     db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
# #     if db_product:
# #         for key, value in product.dict().items():
# #             setattr(db_product, key, value)
# #         db.commit()
# #         db.refresh(db_product)
# #     return db_product

# # def delete_product(db: Session, product_id: int):
# #     db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
# #     if db_product:
# #         db.delete(db_product)
# #         db.commit()
# #     return db_product

from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, name: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = models.User(name=name, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product: schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        for key, value in product.dict().items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
