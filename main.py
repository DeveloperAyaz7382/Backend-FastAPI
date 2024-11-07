from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from crud import create_user, authenticate_user, create_product, get_product, get_products, update_product, delete_product
import schemas
import models
from pathlib import Path
import shutil
import logging

# Create the tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Directory to store uploaded images
UPLOAD_DIRECTORY = Path("uploaded_images/")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

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

# Create Product Endpoint
@app.post("/products/", response_model=schemas.Product)
async def create_product_endpoint(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)

# Upload Image Endpoint
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_location = UPLOAD_DIRECTORY / file.filename
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": str(file_location)}

# Create Product with Image Endpoint
@app.post("/products/with-image/", response_model=schemas.Product)
async def create_product_with_image(
    product: schemas.ProductCreate, 
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save the image
    file_location = UPLOAD_DIRECTORY / image.filename
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Add image URL to product data
    product_data = product.dict()
    product_data["image_url"] = str(file_location)

    # Create product
    return create_product(db=db, product=schemas.ProductCreate(**product_data))

# Get Product by ID
@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Get List of Products
@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_products(db, skip=skip, limit=limit)

# Update Product
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product_endpoint(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    updated_product = update_product(db=db, product_id=product_id, product=product)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

# Delete Product
@app.delete("/products/{product_id}")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    deleted_product = delete_product(db=db, product_id=product_id)
    if deleted_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
