from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import add_user, validate_user
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "f7e8a9d8c2e1f0b7a3d4e9c0f1a2b7c9e5d6f8a3e7b0c5d1f3a8b4c6d9e0a1f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignUpInput(BaseModel):
    username: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/signup/")
async def signup(input: SignUpInput):
    if add_user(input.username, input.password):
        return {"message": f"User {input.username} registered successfully"}
    raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/token/")
async def login(input: LoginInput):
    if not validate_user(input.username, input.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": input.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/user/")
async def get_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
