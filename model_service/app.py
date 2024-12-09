from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests
from transformers import pipeline
import os



app = FastAPI()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
# loading the model for the emotion detection
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")


class TextInput(BaseModel):
    text: str

# endpoint for prediction
@app.post("/predict/")
async def predict_emotion(input: TextInput, authorization: str = Header(...)):
    # Step 1: Verify the Authorization header
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    # Step 2: Extract and log the token (no validation for now)
    token = authorization.split(" ")[1]
    print(f"Received Token: {token}")

    # Step 3: Pass the text to the model for prediction
    try:
        prediction = emotion_classifier(input.text)
        return {
            "text": input.text,
            "emotion": prediction[0]["label"],
            "confidence": prediction[0]["score"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")