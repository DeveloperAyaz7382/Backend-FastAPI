from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form ,Request   # Add Form here
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
import logging  # Import the logging module at the start of the script


# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product API with Image Upload")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logging.basicConfig(level=logging.INFO)  # Initialize logging

# Configure CORS
origins = ["http://localhost:5173"]  # Update with your frontend URL if necessary

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response

# API Endpoints

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



# Define the path to save uploaded images
UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-image/", summary="Upload an image", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    # Validate the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    # Create a unique filename to prevent conflicts
    filename = f"{os.urandom(16).hex()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # In a real application, you'd probably serve these files via a CDN or dedicated static file server
    image_url = f"/images/{filename}"
    
    return {"image_url": image_url}

@app.post("/products/", response_model=schemas.Product, summary="Create a new product")
def create_product_endpoint(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    compare_at_price: Optional[float] = Form(None),
    cost_per_item: Optional[float] = Form(None),
    quantity: int = Form(0),
    category: Optional[str] = Form(None),
    vendor: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_url = None
    if image:
        # Validate image type
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file is not an image")
        
        # Create a unique filename
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
        quantity=quantity,
        category=category,
        vendor=vendor,
        sku=sku,
        barcode=barcode,
        tags=tags,
        image_url=image_url
    )
    
    product = crud.create_product(db=db, product=product_data)
    return product

@app.get("/products/", response_model=List[schemas.Product], summary="Get all products")
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product, summary="Get a product by ID")
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product, summary="Update a product by ID")
def update_product_endpoint(
    product_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    compare_at_price: Optional[float] = Form(None),
    cost_per_item: Optional[float] = Form(None),
    quantity: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    vendor: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
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
        
        # Optionally, delete the old image file
        if image_url:
            old_image_path = image_url.lstrip("/")
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
        
        # Save the new image
        filename = f"{os.urandom(16).hex()}_{image.filename}"
        file_location = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_url = f"/images/{filename}"
    
    # Prepare the updated data
    updated_data = schemas.ProductCreate(
        title=title if title is not None else product.title,
        description=description if description is not None else product.description,
        price=price if price is not None else product.price,
        compare_at_price=compare_at_price if compare_at_price is not None else product.compare_at_price,
        cost_per_item=cost_per_item if cost_per_item is not None else product.cost_per_item,
        quantity=quantity if quantity is not None else product.quantity,
        category=category if category is not None else product.category,
        vendor=vendor if vendor is not None else product.vendor,
        sku=sku if sku is not None else product.sku,
        barcode=barcode if barcode is not None else product.barcode,
        tags=tags if tags is not None else product.tags,
        image_url=image_url
    )
    
    updated_product = crud.update_product(db=db, product_id=product_id, product=updated_data)
    return updated_product

@app.delete("/products/{product_id}", response_model=schemas.Product, summary="Delete a product by ID")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = crud.delete_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Optionally, delete the associated image file
    if product.image_url:
        image_path = product.image_url.lstrip("/")
        if os.path.isfile(image_path):
            os.remove(image_path)
    
    return product

# Serve images
@app.get("/images/{image_filename}", response_class=FileResponse, summary="Get an image by filename")
def get_image(image_filename: str):
    file_path = os.path.join(UPLOAD_DIR, image_filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)



# # Create Product Endpoint
# @app.post("/products/", response_model=schemas.Product)
# async def create_product_endpoint(product: schemas.ProductCreate, db: Session = Depends(get_db)):
#     return create_product(db=db, product=product)

# # Upload Image Endpoint
# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     file_location = UPLOAD_DIRECTORY / file.filename
#     with file_location.open("wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"image_url": str(file_location)}

# # Create Product with Image Endpoint
# @app.post("/products/with-image/", response_model=schemas.Product)
# async def create_product_with_image(
#     product: schemas.ProductCreate, 
#     image: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     # Save the image
#     file_location = UPLOAD_DIRECTORY / image.filename
#     with file_location.open("wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)
    
#     # Add image URL to product data
#     product_data = product.dict()
#     product_data["image_url"] = str(file_location)

#     # Create product
#     return create_product(db=db, product=schemas.ProductCreate(**product_data))

# # Get Product by ID
# @app.get("/products/{product_id}", response_model=schemas.Product)
# def read_product(product_id: int, db: Session = Depends(get_db)):
#     db_product = get_product(db, product_id=product_id)
#     if db_product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return db_product

# # Get List of Products
# @app.get("/products/", response_model=list[schemas.Product])
# def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return get_products(db, skip=skip, limit=limit)

# # Update Product
# @app.put("/products/{product_id}", response_model=schemas.Product)
# def update_product_endpoint(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
#     updated_product = update_product(db=db, product_id=product_id, product=product)
#     if updated_product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return updated_product

# # Delete Product
# @app.delete("/products/{product_id}")
# def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
#     deleted_product = delete_product(db=db, product_id=product_id)
#     if deleted_product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return {"message": "Product deleted successfully"}



