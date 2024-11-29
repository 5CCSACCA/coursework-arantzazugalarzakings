from fastapi import FastAPI, HTTPException, Depends, Header
from transformers import pipeline
from datetime import datetime
import requests
import os
from pydantic import BaseModel

# Initialize the FastAPI application
app = FastAPI()

# Get the authentication service URL from environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

# Set up the emotion classification pipeline using Hugging Face
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# Define the input model for text
class TextInput(BaseModel):  # Using BaseModel for input validation
    text: str

# Function to fetch the current user by calling the authentication service
def get_current_user(authorization: str = Header(...)):
    response = requests.get(f"{AUTH_SERVICE_URL}/user", headers={"Authorization": authorization})
    if response.status_code == 200:  # User successfully authenticated
        return response.json()
    else:  # Authentication failed
        raise HTTPException(status_code=401, detail="Authentication failed")

# Endpoint to predict the emotion of the given text
@app.post("/predict/")
async def predict_emotion(input: TextInput, authorization: str = Header(None)):
    # Check if the Authorization header is received
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header is missing")
    
    print("Authorization Header Received:", authorization)
    
    # Validate the user by calling the authentication service
    user = get_current_user(authorization)

    # Perform emotion classification on the input text
    result = emotion_classifier(input.text)

    # Prepare the log entry with prediction details
    log_entry = {
        "username": user["username"],  # Username retrieved from authentication service
        "text": input.text,            # Text provided by the user
        "emotion": result[0]["label"], # Predicted emotion
        "confidence": result[0]["score"],  # Confidence score of the prediction
        "timestamp": datetime.utcnow().isoformat(),  # Timestamp of the prediction
    }

    # Print the log entry (optional: save it to a database)
    print("Log Entry:", log_entry)

    # Return the prediction result to the user
    return {
        "text": input.text,            # Original input text
        "emotion": result[0]["label"], # Predicted emotion
        "confidence": result[0]["score"],  # Confidence score
        "log": log_entry,              # Log details for reference
    }
