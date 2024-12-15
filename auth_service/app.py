from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

@app.post("/signup/", summary="Register a new user")
async def signup(username: str = Form(...), password: str = Form(...)):
    """
    Register a new user by providing a username and password.
    """
    hashed_password = pwd_context.hash(password)
    return {"message": f"User {username} has been registered successfully", "password_hash": hashed_password}

@app.post("/login/", summary="Login user")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Login with username and password to obtain a JWT token.
    """
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/whoami/", summary="Validate token")
async def whoami(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Validate the JWT token and return the username.
    """
    token = credentials.credentials
    username = decode_access_token(token)
    return {"username": username}

@app.get("/health/", summary="Health Check")
async def health_check():
    """
    Check the service health.
    """
    return {"status": "ok"}
