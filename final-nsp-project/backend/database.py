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


def _ensure_dns_resolver():
    """
    mongodb+srv:// URLs need a DNS lookup. dnspython derives its default
    domain from the machine hostname and crashes if that contains characters
    IDNA can't encode (e.g. an emoji in a Windows computer name). In that case
    build the resolver against a plain hostname and public nameservers.
    """
    try:
        import dns.resolver
    except ImportError:
        return
    try:
        dns.resolver.get_default_resolver()
    except Exception:
        import socket
        real_gethostname = socket.gethostname
        socket.gethostname = lambda: "localhost"
        try:
            resolver = dns.resolver.Resolver(configure=False)
        finally:
            socket.gethostname = real_gethostname
        resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
        dns.resolver.default_resolver = resolver


if MONGODB_URL.startswith("mongodb+srv://"):
    _ensure_dns_resolver()

if MONGODB_URL == "memory":
    # Local development without a reachable Atlas cluster: an in-memory
    # MongoDB (data is lost on restart). Requires `pip install mongomock-motor`.
    from mongomock_motor import AsyncMongoMockClient
    client = AsyncMongoMockClient()
else:
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
