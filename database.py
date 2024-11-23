from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)

# Database and collections
db = client["user_management"]  # Main database
users_collection = db["users"]  # User credentials
logs_collection = db["logs"]  # Logs for predictions
