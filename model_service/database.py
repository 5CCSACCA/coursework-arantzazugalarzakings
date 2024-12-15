import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongodb:27017/emotion_service?authSource=admin")
MONGO_DB_NAME = "emotion_service"

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
predictions_collection = db["predictions"]

# Helper functions
def save_prediction(username: str, text: str, emotion: str, confidence: float):
    """
    Save a prediction to the database.
    """
    predictions_collection.insert_one({
        "username": username,
        "text": text,
        "emotion": emotion,
        "confidence": confidence,
        "timestamp": datetime.utcnow()
    })

def get_statistics():
    """
    Retrieve overall statistics for predictions.
    """
    total_predictions = predictions_collection.count_documents({})
    emotions_count = predictions_collection.aggregate([
        {"$group": {"_id": "$emotion", "count": {"$sum": 1}}}
    ])
    emotions_count = {doc["_id"]: doc["count"] for doc in emotions_count}
    most_common_emotion = max(emotions_count, key=emotions_count.get, default=None)
    return {
        "total_predictions": total_predictions,
        "emotions_count": emotions_count,
        "most_common_emotion": most_common_emotion,
    }

def get_user_history(username: str):
    """
    Retrieve all predictions for a specific user.
    """
    user_history = predictions_collection.find({"username": username}).sort("timestamp", -1)
    return [
        {
            "text": doc["text"],
            "emotion": doc["emotion"],
            "timestamp": doc["timestamp"].isoformat()
        }
        for doc in user_history
    ]
