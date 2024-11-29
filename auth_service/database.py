# database.py
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB setup
MONGO_URI = os.getenv(
    "MONGO_URI", 
    "mongodb://root:example@mongodb:27017/emotion_detection?authSource=admin"
)

# Connect to the MongoDB client
client = MongoClient(MONGO_URI)
db = client["emotion_detection"]
users_collection = db["users"]

def add_user(username: str, password: str) -> bool:
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

def validate_user(username: str, password: str) -> bool:
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False
