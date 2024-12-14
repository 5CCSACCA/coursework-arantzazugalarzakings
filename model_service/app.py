from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from transformers import pipeline
import httpx
from fine_tune import fine_tune_model

# FastAPI app
app = FastAPI()

# Define the security scheme for the `Authorization` header
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

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
                f"{AUTH_SERVICE_URL}/user/",
                json={"token": token},
            )
            response.raise_for_status()
            return response.json()["username"]
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {http_err.response.text}")
    except httpx.RequestError as err:
        raise HTTPException(status_code=500, detail=f"Error connecting to Auth Service: {err}")

@app.post("/predict/")
async def predict_emotion(
    input: TextInput,
    authorization: str = Depends(api_key_header),  # Use FastAPI's APIKeyHeader
):
    # Validate the token via the Auth Service
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization header format. Expected 'Bearer <token>'.")
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

@app.post("/fine-tune/")
async def fine_tune(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger model fine-tuning.
    """
    background_tasks.add_task(fine_tune_model)  # Run fine-tuning in the background
    return {"message": "Fine-tuning started. Check MLflow for progress."}

@app.get("/health/")
async def health_check():
    return {"status": "ok"}
