from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB setup
client = MongoClient("mongodb://mongodb:27017/")
db = client["emotion_detection"]
users_collection = db["users"]
logs_collection = db["logs"]

# Add a new user
def add_user(username: str, password: str):
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    hashed_password = generate_password_hash(password)  # Hash the password
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# Validate user credentials
def validate_user(username: str, password: str) -> bool:
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False

# Log predictions
def log_prediction(log_entry: dict):
    logs_collection.insert_one(log_entry)
