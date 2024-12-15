from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

# Security scheme for Swagger UI
bearer_scheme = HTTPBearer()

# Helper functions
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Generate a JWT access token.
    """
    if "sub" not in data:
        raise ValueError("Token payload must include 'sub'")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """
    Decode the JWT token and validate it.
    """
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

@app.post("/signup/")
async def signup(input: SignUpInput):
    """
    Endpoint to handle user signup.
    """
    # Placeholder implementation (database integration can be added later)
    hashed_password = pwd_context.hash(input.password)
    return {"message": f"User {input.username} has been registered successfully", "password_hash": hashed_password}

@app.post("/login/", response_model=Token)
async def login(input: LoginInput):
    """
    Endpoint to handle user login and return a JWT token.
    """
    # Placeholder: Assume all users are valid for demonstration
    access_token = create_access_token(
        data={"sub": input.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/whoami/", response_model=dict)
async def whoami(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Endpoint to validate the JWT and return the username.
    Uses Authorization: Bearer <token> header.
    """
    token = credentials.credentials
    username = decode_access_token(token)
    return {"username": username}

@app.get("/health/")
async def health_check():
    """
    Health check endpoint to ensure the service is running.
    """
    return {"status": "ok"}
