# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from crud import create_user, authenticate_user
from models import User
from pydantic import BaseModel
import logging
from fastapi import Request

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # Update with your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
    
@app.get("/")
def welcome():
    return {"message": "Welcome to FastAPI!"}

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = create_user(db, user.name, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="User registration failed")
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}
