from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import requests

app = FastAPI()

# External service URLs
AUTH_SERVICE_URL = "http://auth-service:8001"
MODEL_SERVICE_URL = "http://model-service:8000"

# Security: Bearer Token
security = HTTPBearer()

# Schemas for requests and responses
class AuthInput(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TextInput(BaseModel):
    text: str

# Helper function to validate token via auth-service
def validate_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    response = requests.post(f"{AUTH_SERVICE_URL}/user/", json={"token": token})
    if response.status_code == 200:
        return response.json()["username"]
    raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")

# Authentication Endpoints
@app.post("/signup/", tags=["Authentication"])
def signup(data: AuthInput):
    """
    User signup endpoint.
    """
    response = requests.post(f"{AUTH_SERVICE_URL}/signup/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/token/", response_model=TokenResponse, tags=["Authentication"])
def token(data: AuthInput):
    """
    Generate authentication token.
    """
    response = requests.post(f"{AUTH_SERVICE_URL}/token/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

# Emotion Detection Endpoints
@app.post("/predict/", tags=["Emotion Detection"])
def predict(data: TextInput, username: str = Depends(validate_token)):
    """
    Predict emotion from text.
    """
    response = requests.post(
        f"{MODEL_SERVICE_URL}/predict/",
        json=data.dict(),
        headers={"Authorization": f"Bearer {username}"},  # Forward the validated token
    )
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/health/", tags=["Emotion Detection"])
def health_check():
    """
    Health check for the service.
    """
    return {"status": "ok"}

# Custom OpenAPI Schema for Titles
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Gateway",
        version="1.0.0",
        description="This API Gateway manages user authentication and emotion detection requests.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    openapi_schema["tags"] = [
        {"name": "Authentication", "description": "Endpoints for user authentication and token management"},
        {"name": "Emotion Detection", "description": "Endpoints for emotion detection tasks"},
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
