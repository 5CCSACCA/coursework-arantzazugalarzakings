from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

# FastAPI app
app = FastAPI()

# Constants
SECRET_KEY = "f7e8a9d8c2e1f0b7a3d4e9c0f1a2b7c9e5d6f8a3e7b0c5d1f3a8b4c6d9e0a1f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper functions
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if "sub" not in data:
        raise ValueError("Token payload must include 'sub'")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload: 'sub' is missing")
        return username
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

# Schemas
class SignUpInput(BaseModel):
    username: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    token: str

@app.post("/signup/")
async def signup(input: SignUpInput):
    return {"message": f"User {input.username} registered successfully"}

@app.post("/token/", response_model=Token)
async def login(input: LoginInput):
    access_token = create_access_token(
        data={"sub": input.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/", response_model=dict)
async def get_user(request: TokenRequest):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

@app.get("/health/")
async def health_check():
    return {"status": "ok"}