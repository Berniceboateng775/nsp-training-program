"""User profile API routes."""

from fastapi import APIRouter, Depends
from auth import get_current_user
from models import ProfileUpdate
from database import users_collection, reading_list_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("")
async def get_profile(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return user


@router.put("")
async def update_profile(
    body: ProfileUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user profile."""
    update_data = {}
    if body.name is not None:
        update_data["name"] = body.name
    if body.favorite_genres is not None:
        update_data["favorite_genres"] = body.favorite_genres
    
    if update_data:
        await users_collection.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": update_data}
        )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(user["id"])})
    return {
        "id": str(updated_user["_id"]),
        "name": updated_user["name"],
        "email": updated_user["email"],
        "favorite_genres": updated_user.get("favorite_genres", []),
        "created_at": updated_user.get("created_at", "")
    }


@router.get("/reading-list")
async def get_reading_list(user: dict = Depends(get_current_user)):
    """Get user's saved reading list."""
    cursor = reading_list_collection.find({"user_id": user["id"]}).sort("added_at", -1)
    books = []
    async for book in cursor:
        books.append({
            "id": str(book["_id"]),
            "title": book["title"],
            "author": book.get("author", ""),
            "genre": book.get("genre", ""),
            "added_at": book.get("added_at", "")
        })
    return {"books": books}


@router.post("/reading-list")
async def add_to_reading_list(
    book: dict,
    user: dict = Depends(get_current_user)
):
    """Add a book to reading list."""
    book_doc = {
        "user_id": user["id"],
        "title": book.get("title", ""),
        "author": book.get("author", ""),
        "genre": book.get("genre", ""),
        "added_at": datetime.utcnow().isoformat()
    }
    await reading_list_collection.insert_one(book_doc)
    return {"message": "Book added to reading list"}
