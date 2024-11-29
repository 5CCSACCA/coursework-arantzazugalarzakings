from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests

app = FastAPI(
    title="Unified API",
    description="""
    This API combines the authentication service (auth-service) and the model service (model-service).
    """,
    version="1.0.0"
)

# Input model for /signup and /token
class AuthInput(BaseModel):
    username: str
    password: str

# Input model for /predict
class TextInput(BaseModel):
    text: str

@app.post("/signup/")
def signup(data: AuthInput):
    response = requests.post("http://auth-service:8001/signup/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/token/")
def token(data: AuthInput):
    response = requests.post("http://auth-service:8001/token/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/predict/")
def predict(data: TextInput, authorization: str = Header(...)):
    headers = {"Authorization": authorization}
    response = requests.post(
        "http://model-service:8000/predict/", json=data.dict(), headers=headers
    )
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)
