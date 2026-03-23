"""
MongoDB connection manager for Vellichor AI.
Uses Motor (async MongoDB driver) for non-blocking database operations.
"""

import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "vellichor"

client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=certifi.where())
database = client[DATABASE_NAME]

# Collections
users_collection = database["users"]
conversations_collection = database["conversations"]
reading_list_collection = database["reading_list"]


async def init_db():
    """Create indexes for optimal query performance."""
    await users_collection.create_index("email", unique=True)
    await conversations_collection.create_index("user_id")
    await reading_list_collection.create_index("user_id")
