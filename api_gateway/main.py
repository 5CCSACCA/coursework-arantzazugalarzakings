from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests

app = FastAPI()

AUTH_SERVICE_URL = "http://auth-service:8001"
MODEL_SERVICE_URL = "http://model-service:8000"

class AuthInput(BaseModel):
    username: str
    password: str

class TextInput(BaseModel):
    text: str

@app.post("/signup/")
def signup(data: AuthInput):
    response = requests.post(f"{AUTH_SERVICE_URL}/signup/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/token/")
def token(data: AuthInput):
    response = requests.post(f"{AUTH_SERVICE_URL}/token/", json=data.dict())
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/predict/")
def predict(data: TextInput, authorization: str = Header(...)):
    response = requests.post(f"{MODEL_SERVICE_URL}/predict/", json=data.dict(), headers={"Authorization": authorization})
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)
