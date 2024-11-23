from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from transformers import pipeline
from database import users_collection, logs_collection
from auth import hash_password, verify_password, create_access_token
from datetime import datetime
from jose import JWTError, jwt

# Initialize FastAPI app
app = FastAPI()

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Load the emotion classifier
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# Input data schema
class TextInput(BaseModel):
    text: str

class User(BaseModel):
    username: str
    password: str

# Dependency for token validation
async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/register")
async def register(user: User):
    # Check if user exists
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password and save user
    hashed_password = hash_password(user.password)
    new_user = {"username": user.username, "hashed_password": hashed_password, "created_at": datetime.utcnow()}
    await users_collection.insert_one(new_user)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: User):
    # Authenticate user
    existing_user = await users_collection.find_one({"username": user.username})
    if not existing_user or not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict/")
async def predict_emotion(input: TextInput, username: str = Depends(get_current_user)):
    # Perform emotion classification
    result = emotion_classifier(input.text)

    # Log prediction
    log_entry = {
        "username": username,
        "text": input.text,
        "emotion": result[0]["label"],
        "confidence": result[0]["score"],
        "timestamp": datetime.utcnow()
    }
    await logs_collection.insert_one(log_entry)

    return {"text": input.text, "emotion": result[0]["label"], "confidence": result[0]["score"]}
