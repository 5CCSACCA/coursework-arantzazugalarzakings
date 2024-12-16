from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from database import save_prediction, get_statistics, get_user_history
import httpx

# FastAPI app
app = FastAPI()

# Constants
AUTH_SERVICE_URL = "http://auth-service:8001"

# Security scheme
bearer_scheme = HTTPBearer()

# Dynamic model loading
MODEL_DIR = "./mlflow_model"
try:
    emotion_classifier = pipeline(
        "text-classification",
        model=AutoModelForSequenceClassification.from_pretrained(MODEL_DIR),
        tokenizer=AutoTokenizer.from_pretrained(MODEL_DIR),
    )
    print("Fine-tuned model loaded successfully!")
except Exception as e:
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base"
    )
    print(f"Using default model: {str(e)}")

# Token validation function
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    async with httpx.AsyncClient() as client:
        token = credentials.credentials
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/whoami/",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()["username"]
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

# Endpoints
@app.post("/predict/", summary="Predict Emotion")
async def predict_emotion(
    text: str = Form(..., description="Input text to analyze for emotions"),
    username: str = Depends(validate_token)
):
    try:
        prediction = emotion_classifier(text)
        emotion = prediction[0]["label"]
        confidence = prediction[0]["score"]
        save_prediction(username, text, emotion, confidence)
        return {"username": username, "text": text, "emotion": emotion, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/stats/", summary="Retrieve Emotion Statistics")
async def get_emotion_statistics(username: str = Depends(validate_token)):
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@app.get("/history/", summary="Retrieve User Emotion History")
async def get_emotion_history(username: str = Depends(validate_token)):
    try:
        history = get_user_history(username)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/health/", summary="Health Check")
async def health_check():
    return {"status": "ok"}
