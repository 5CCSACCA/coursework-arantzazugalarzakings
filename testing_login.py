from database import users_collection
from auth import hash_password
from datetime import datetime
import asyncio

async def create_test_user():
    # Test user data
    username = "aran"
    password = "galarza"

    # Check if user already exists
    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        print("Test user already exists.")
        return

    # Hash the password
    hashed_password = hash_password(password)

    # Insert the user into the database
    new_user = {
        "username": username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }
    await users_collection.insert_one(new_user)
    print("Test user created successfully.")

# Run the function to create the user
if __name__ == "__main__":
    asyncio.run(create_test_user())
