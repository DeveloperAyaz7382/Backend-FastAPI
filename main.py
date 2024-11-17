
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from crud import create_user, authenticate_user
from pathlib import Path
import os
import shutil
from typing import List, Optional
from fastapi.responses import FileResponse
import models, schemas, crud
from database import engine, SessionLocal
import logging

# Initialize and configure the app
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product API with Image Upload")

# Configure CORS for frontend interaction
origins = ["http://localhost:5173"]  # Update with your frontend URL if necessary
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload directory for images
UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Welcome endpoint
@app.get("/")
def welcome():
    return {"message": "Welcome to FastAPI!"}

# User Registration Endpoint
@app.post("/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = create_user(db, user.name, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="User registration failed")
    return {"message": "User registered successfully"}

# User Login Endpoint
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}

# Product CRUD Endpoints

@app.get("/products/", response_model=List[schemas.Product], summary="Get all products")
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=schemas.Product, summary="Get a product by ID")
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products/", response_model=schemas.Product, summary="Create a new product")
def create_product_endpoint(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    compare_at_price: Optional[float] = Form(None),
    cost_per_item: Optional[float] = Form(None),
    profit: Optional[float] = Form(None),
    margin: Optional[float] = Form(None),
    track_quantity: Optional[bool] = Form(None),
    status: Optional[str] = Form(None),
    sales_channels: Optional[str] = Form(None),
    markets: Optional[str] = Form(None),
    product_type: Optional[str] = Form(None),
    vendor: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    collections: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not an image")
        filename = f"{os.urandom(16).hex()}_{image.filename}"
        file_location = os.path.join(UPLOAD_DIR, filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/images/{filename}"
    
    product_data = schemas.ProductCreate(
        title=title,
        description=description,
        price=price,
        compare_at_price=compare_at_price,
        cost_per_item=cost_per_item,
        profit=profit,
        margin=margin,
        track_quantity=track_quantity,
        status=status,
        sales_channels=sales_channels,
        markets=markets,
        product_type=product_type,
        vendor=vendor,
        sku=sku,
        barcode=barcode,
        collections=collections,
        tags=tags,
        image_url=image_url
    )
    
    product = crud.create_product(db=db, product=product_data)
    return product

@app.put("/products/{product_id}", response_model=schemas.Product, summary="Update a product by ID")
def update_product_endpoint(
    product_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    compare_at_price: Optional[float] = Form(None),
    cost_per_item: Optional[float] = Form(None),
    profit: Optional[float] = Form(None),
    margin: Optional[float] = Form(None),
    track_quantity: Optional[bool] = Form(None),
    status: Optional[str] = Form(None),
    sales_channels: Optional[str] = Form(None),
    markets: Optional[str] = Form(None),
    product_type: Optional[str] = Form(None),
    vendor: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    collections: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    image_url = product.image_url
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not an image")
        if image_url:
            old_image_path = image_url.lstrip("/")
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
        filename = f"{os.urandom(16).hex()}_{image.filename}"
        file_location = os.path.join(UPLOAD_DIR, filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/images/{filename}"
    
    updated_product = crud.update_product(
        db=db, product_id=product_id, product=schemas.ProductCreate(
            title=title or product.title,
            description=description or product.description,
            price=price or product.price,
            compare_at_price=compare_at_price if compare_at_price is not None else product.compare_at_price,
            cost_per_item=cost_per_item or product.cost_per_item,
            profit=profit or product.profit,
            margin=margin or product.margin,
            track_quantity=track_quantity if track_quantity is not None else product.track_quantity,
            status=status or product.status,
            sales_channels=sales_channels or product.sales_channels,
            markets=markets or product.markets,
            product_type=product_type or product.product_type,
            vendor=vendor or product.vendor,
            sku=sku or product.sku,
            barcode=barcode or product.barcode,
            collections=collections or product.collections,
            tags=tags or product.tags,
            image_url=image_url
        )
    )
    return updated_product

@app.delete("/products/{product_id}", response_model=schemas.Product, summary="Delete a product by ID")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.delete_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.image_url:
        image_path = product.image_url.lstrip("/")
        if os.path.isfile(image_path):
            os.remove(image_path)
    return product
