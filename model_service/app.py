from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import httpx
import os
from fine_tune import fine_tune_model
from database import save_prediction, get_statistics, get_user_history

# FastAPI app
app = FastAPI()

# Bearer token scheme for authentication
bearer_scheme = HTTPBearer()

# Dynamic model loading
MODEL_DIR = "./mlflow_model"
try:
    # Try to load the fine-tuned model
    emotion_classifier = pipeline(
        "text-classification",
        model=AutoModelForSequenceClassification.from_pretrained(MODEL_DIR),
        tokenizer=AutoTokenizer.from_pretrained(MODEL_DIR),
    )
    print("Fine-tuned model loaded successfully!")
except Exception as e:
    # Fall back to the default pre-trained model
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base"
    )
    print(f"Using default model: {str(e)}")

# Schemas
class TextInput(BaseModel):
    text: str

AUTH_SERVICE_URL = "http://auth-service:8001"

# Helper function to validate token with Auth Service
async def validate_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Validate the Bearer token with the auth-service's /whoami/ endpoint.
    """
    token = credentials.credentials
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/whoami/",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()["username"]
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Error connecting to Auth Service")

# Endpoints
@app.post("/predict-emotions/")
async def predict_emotion(input: TextInput, username: str = Depends(validate_token)):
    """
    Predict the emotion of the input text.
    """
    try:
        prediction = emotion_classifier(input.text)
        emotion = prediction[0]["label"]
        confidence = prediction[0]["score"]

        # Save the prediction in MongoDB
        save_prediction(username, input.text, emotion, confidence)

        return {
            "username": username,
            "text": input.text,
            "emotion": emotion,
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/statistics-emotions/")
async def get_statistics_endpoint(username: str = Depends(validate_token)):
    """
    Retrieve overall statistics for predictions.
    """
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@app.get("/emotions-history/")
async def get_user_history_endpoint(username: str = Depends(validate_token)):
    """
    Retrieve user-specific emotion prediction history.
    """
    try:
        history = get_user_history(username)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.post("/fine-tune/")
async def fine_tune(background_tasks: BackgroundTasks, username: str = Depends(validate_token)):
    """
    Trigger model fine-tuning in the background.
    """
    try:
        background_tasks.add_task(fine_tune_model)
        return {"message": "Fine-tuning started. Check MLflow for progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fine-tuning failed: {str(e)}")

@app.get("/health/")
async def health_check():
    """
    Check the health of the service.
    """
    return {"status": "ok"}
