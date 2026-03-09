"""
Book Recommendation API routes — powered by Open Library.
Provides personalized recommendations, search, and book details.
"""

import httpx
import logging
from fastapi import APIRouter, Depends, Query
from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])

OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"
OPEN_LIBRARY_WORKS = "https://openlibrary.org"


def _format_book(doc: dict) -> dict:
    """Convert an Open Library search result into our book format."""
    cover_id = doc.get("cover_i")
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
    
    # Get the Open Library work key for details page
    key = doc.get("key", "")  # e.g., "/works/OL45804W"
    
    return {
        "title": doc.get("title", "Unknown Title"),
        "author": ", ".join(doc.get("author_name", ["Unknown Author"])[:2]),
        "genre": (doc.get("subject", [])[:3] if doc.get("subject") else ["General"]),
        "description": doc.get("first_sentence", [""])[0] if doc.get("first_sentence") else "",
        "cover_url": cover_url,
        "year": doc.get("first_publish_year"),
        "rating": round(doc.get("ratings_average", 0), 1) if doc.get("ratings_average") else None,
        "pages": doc.get("number_of_pages_median"),
        "ol_key": key,
        "editions": doc.get("edition_count", 0),
        "languages": doc.get("language", [])[:5],
    }


async def _search_open_library(query: str = None, subject: str = None, limit: int = 12) -> list:
    """Search Open Library by query or subject."""
    params = {"limit": limit, "fields": "key,title,author_name,cover_i,first_publish_year,subject,first_sentence,ratings_average,number_of_pages_median,edition_count,language"}
    
    if query:
        params["q"] = query
    elif subject:
        params["subject"] = subject.lower()
    else:
        params["q"] = "popular fiction"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(OPEN_LIBRARY_SEARCH, params=params)
            resp.raise_for_status()
            data = resp.json()
            return [_format_book(doc) for doc in data.get("docs", [])[:limit]]
    except Exception as e:
        logger.error(f"Open Library search error: {e}")
        return []


# ─── Recommendations (based on user genres) ──────────────────

@router.get("/trending")
async def get_trending():
    """Get trending books from Open Library."""
    books = await _search_open_library(query="bestseller fiction 2024", limit=12)
    if not books:
        books = await _search_open_library(query="popular novels", limit=12)
    return {"books": books}


@router.post("")
async def get_recommendations(user: dict = Depends(get_current_user)):
    """Get personalized recommendations based on user's favorite genres."""
    genres = user.get("favorite_genres", [])
    
    all_books = []
    if genres:
        # Fetch books for each favorite genre
        for genre in genres[:3]:  # Max 3 genres to keep it fast
            genre_books = await _search_open_library(subject=genre, limit=6)
            all_books.extend(genre_books)
    
    if not all_books:
        all_books = await _search_open_library(query="popular fiction", limit=12)
    
    # Remove duplicates by title
    seen = set()
    unique_books = []
    for book in all_books:
        if book["title"] not in seen:
            seen.add(book["title"])
            unique_books.append(book)
    
    return {"books": unique_books[:12]}


# ─── Search ──────────────────────────────────────────────────

@router.get("/search")
async def search_books(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(12, ge=1, le=50)
):
    """Search Open Library for books by title, author, or keyword."""
    books = await _search_open_library(query=q, limit=limit)
    return {"books": books, "query": q, "total": len(books)}


# ─── Book Details ────────────────────────────────────────────

@router.get("/book/{work_id}")
async def get_book_details(work_id: str):
    """
    Get detailed info about a specific book from Open Library.
    work_id is like 'OL45804W' (without the /works/ prefix).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get work details
            resp = await client.get(f"{OPEN_LIBRARY_WORKS}/works/{work_id}.json")
            resp.raise_for_status()
            work = resp.json()
            
            # Get edition info for cover + pages
            editions_resp = await client.get(
                f"{OPEN_LIBRARY_WORKS}/works/{work_id}/editions.json",
                params={"limit": 5}
            )
            editions = editions_resp.json().get("entries", []) if editions_resp.status_code == 200 else []
        
        # Extract description
        description = work.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")
        
        # Get cover
        covers = work.get("covers", [])
        cover_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg" if covers else None
        
        # Get subjects
        subjects = work.get("subjects", [])[:10]
        
        # Get author names
        author_keys = [a.get("author", {}).get("key", "") for a in work.get("authors", [])]
        authors = []
        for key in author_keys[:3]:
            if key:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        author_resp = await client.get(f"{OPEN_LIBRARY_WORKS}{key}.json")
                        if author_resp.status_code == 200:
                            authors.append(author_resp.json().get("name", "Unknown"))
                except Exception:
                    pass
        
        # First publish date from editions
        first_year = None
        pages = None
        for ed in editions:
            if ed.get("publish_date") and not first_year:
                first_year = ed.get("publish_date")
            if ed.get("number_of_pages") and not pages:
                pages = ed.get("number_of_pages")
        
        return {
            "title": work.get("title", "Unknown"),
            "authors": authors or ["Unknown Author"],
            "description": description,
            "cover_url": cover_url,
            "subjects": subjects,
            "first_published": first_year,
            "pages": pages,
            "ol_key": f"/works/{work_id}",
            "ol_url": f"https://openlibrary.org/works/{work_id}",
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Open Library API error: {e}")
        return {"error": f"Book not found: {work_id}"}
    except Exception as e:
        logger.error(f"Book details error: {e}")
        return {"error": str(e)}
