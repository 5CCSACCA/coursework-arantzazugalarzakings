from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from transformers import pipeline
import httpx

# FastAPI app
app = FastAPI()

# Load emotion classification model
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# Schemas
class TextInput(BaseModel):
    text: str

AUTH_SERVICE_URL = "http://auth-service:8001"  # Update to the correct URL of your auth service

# Helper function to validate token via Auth Service
async def validate_token_with_auth_service(token: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/whoami",
                json={"token": token},
            )
            response.raise_for_status()  # Raise an exception if the response status is not 200
            return response.json()["username"]
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {http_err}")
    except httpx.RequestError as err:
        raise HTTPException(status_code=500, detail=f"Error connecting to Auth Service: {err}")

@app.post("/predict/")
async def predict_emotion(input: TextInput, authorization: str = Header(...)):
    # Validate the token via the Auth Service
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization header format")
    token = authorization.split(" ")[1]
    username = await validate_token_with_auth_service(token)

    # Perform emotion prediction
    try:
        prediction = emotion_classifier(input.text)
        return {
            "username": username,
            "text": input.text,
            "emotion": prediction[0]["label"],
            "confidence": prediction[0]["score"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health/")
async def health_check():
    return {"status": "ok"}
