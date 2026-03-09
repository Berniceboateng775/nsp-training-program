"""
Vellichor AI — PDF Processing & FAISS Retrieval
=================================================
Handles:
  1. PDF text extraction (via PyMuPDF)
  2. Text chunking (via langchain RecursiveCharacterTextSplitter)
  3. Embedding + FAISS indexing (via sentence-transformers + faiss-cpu)
  4. Semantic query retrieval (top-k chunk search)
"""

import logging
import numpy as np
import fitz  # PyMuPDF
import faiss
from typing import List, Dict, Any, Optional, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.nlp_models import compute_embeddings, compute_single_embedding

logger = logging.getLogger(__name__)

# ─── In-memory session storage for FAISS indexes ───────────
# Maps session_id -> {"index": faiss.Index, "chunks": List[str], "metadata": dict}
_session_stores: Dict[str, Dict[str, Any]] = {}


# ─── PDF Text Extraction ───────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.
    Args:
        pdf_bytes: Raw PDF file bytes
    Returns:
        Full text content as a single string
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages.append(text)
    doc.close()

    full_text = "\n\n".join(pages)
    logger.info(f"Extracted {len(pages)} pages, {len(full_text)} characters from PDF")
    return full_text


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from a plain text file."""
    return content.decode("utf-8", errors="ignore")


# ─── Text Chunking ──────────────────────────────────────────

def chunk_text(
    text: str,
    chunk_size: int = 600,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks for embedding.
    Uses RecursiveCharacterTextSplitter for intelligent splitting
    at paragraph/sentence boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
    )

    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks


# ─── FAISS Indexing ─────────────────────────────────────────

def build_faiss_index(chunks: List[str]) -> Tuple[faiss.Index, np.ndarray]:
    """
    Embed text chunks and build a FAISS index for similarity search.
    Returns:
        (faiss_index, embeddings_array)
    """
    if not chunks:
        raise ValueError("No chunks to index")

    # Compute embeddings (384-dim from MiniLM-L6-v2)
    embeddings = compute_embeddings(chunks)
    embeddings = np.array(embeddings, dtype="float32")

    # Build FAISS index (Inner Product for normalized vectors = cosine similarity)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    logger.info(f"Built FAISS index with {index.ntotal} vectors (dim={dimension})")
    return index, embeddings


def query_faiss(
    index: faiss.Index,
    chunks: List[str],
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search the FAISS index for chunks most similar to the query.
    Returns list of {chunk, score, index} dicts.
    """
    query_embedding = compute_single_embedding(query)
    query_vector = np.array([query_embedding], dtype="float32")

    scores, indices = index.search(query_vector, min(top_k, len(chunks)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0:  # FAISS returns -1 for empty slots
            results.append({
                "chunk": chunks[idx],
                "score": float(score),
                "index": int(idx)
            })

    return results


# ─── Session Management ────────────────────────────────────

def process_document(
    session_id: str,
    file_bytes: bytes,
    filename: str,
    chunk_size: int = 600,
    chunk_overlap: int = 100
) -> Dict[str, Any]:
    """
    Full pipeline: extract text -> chunk -> embed -> index -> store.
    Returns metadata about the processed document.
    """
    # Determine file type and extract text
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif ext in ("txt", "text"):
        text = extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

    if len(text.strip()) < 50:
        raise ValueError("Document contains too little text to analyze")

    # Chunk the text
    chunks = chunk_text(text, chunk_size, chunk_overlap)

    # Build FAISS index
    index, embeddings = build_faiss_index(chunks)

    # Store in session
    _session_stores[session_id] = {
        "index": index,
        "chunks": chunks,
        "filename": filename,
        "full_text": text,
        "total_chars": len(text),
        "total_chunks": len(chunks)
    }

    logger.info(f"Document processed for session {session_id}: {filename} -> {len(chunks)} chunks")

    return {
        "filename": filename,
        "total_characters": len(text),
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "status": "indexed"
    }


def retrieve_context(session_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks for a user query from the session's FAISS index.
    """
    store = _session_stores.get(session_id)
    if not store:
        return []

    return query_faiss(store["index"], store["chunks"], query, top_k)


def get_session_chunks(session_id: str) -> List[str]:
    """Get all chunks for a session (for bulk analysis)."""
    store = _session_stores.get(session_id)
    return store["chunks"] if store else []


def get_session_text(session_id: str) -> Optional[str]:
    """Get the full extracted text for a session."""
    store = _session_stores.get(session_id)
    return store["full_text"] if store else None


def clear_session(session_id: str):
    """Remove a session's FAISS index and data from memory."""
    if session_id in _session_stores:
        del _session_stores[session_id]
        logger.info(f"Cleared session {session_id}")


def session_exists(session_id: str) -> bool:
    """Check if a session has a loaded document."""
    return session_id in _session_stores
