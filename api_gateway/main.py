from fastapi import FastAPI, HTTPException, Depends, Security, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests

# FastAPI app
app = FastAPI()

# External service URLs
AUTH_SERVICE_URL = "http://auth-service:8001"
MODEL_SERVICE_URL = "http://model-service:8000"

# Security: Bearer Token
security = HTTPBearer()

# Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PredictEmotionResponse(BaseModel):
    username: str
    text: str
    emotion: str
    confidence: float

# Helper function to forward requests to services
def forward_request(service_url: str, endpoint: str, method: str = "POST", data: dict = None, headers: dict = None):
    url = f"{service_url}{endpoint}"
    try:
        response = requests.request(method, url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to {url}: {str(e)}")

# Validate token function
def validate_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validate token by calling the Auth Service's /whoami/ endpoint.
    """
    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{AUTH_SERVICE_URL}/whoami/", headers=headers)
    if response.status_code == 200:
        return response.json()["username"]
    raise HTTPException(status_code=403, detail="Invalid or expired token.")

# Authentication Endpoints
@app.post("/signup/", tags=["Authentication"])
def signup(username: str = Form(...), password: str = Form(...)):
    """
    User signup endpoint.
    """
    return forward_request(AUTH_SERVICE_URL, "/signup/", data={"username": username, "password": password})

@app.post("/login/", response_model=TokenResponse, tags=["Authentication"])
def login(username: str = Form(...), password: str = Form(...)):

    return forward_request(AUTH_SERVICE_URL, "/login/", data={"username": username, "password": password})

@app.post("/whoami/", tags=["Authentication"])
def whoami(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    return forward_request(AUTH_SERVICE_URL, "/whoami/", method="POST", headers=headers)

# Emotion Detection Endpoints
@app.post("/detection-emotions/", response_model=PredictEmotionResponse, tags=["Emotion Detection"])
def predict_emotion(text: str = Form(...), credentials: HTTPAuthorizationCredentials = Security(security)):
 
    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    return forward_request(MODEL_SERVICE_URL, "/detection-emotions/", data={"text": text}, headers=headers)

@app.get("/statistics-emotions/", tags=["Emotion Detection"])
def get_statistics(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    return forward_request(MODEL_SERVICE_URL, "/statistics-emotions/", method="GET", headers=headers)

@app.get("/history-emotions/", tags=["Emotion Detection"])
def get_user_history(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    return forward_request(MODEL_SERVICE_URL, "/history-emotions/", method="GET", headers=headers)

