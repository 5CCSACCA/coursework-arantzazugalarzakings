from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

# Initialize FastAPI app
app = FastAPI()

# Load the emotion classifier
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# Input data schema
class TextInput(BaseModel):
    text: str

@app.post("/predict/")
def predict_emotion(input: TextInput):
    result = emotion_classifier(input.text)
    return {"text": input.text, "emotion": result[0]["label"], "confidence": result[0]["score"]}
