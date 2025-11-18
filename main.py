import os
import secrets
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Song, Session

app = FastAPI(title="Project One Setlist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility

def collection(name: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    return db[name]

# Seed default songs if none exist
DEFAULT_SONGS = [
    {"title": "Life Beyond Earth", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "The Story Unfolds", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "The Art of Creation", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "The World Is Yours", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "Numbers", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "Fantasy or Reality", "artist": "Project One", "performed": False, "year": 2008},
    {"title": "It’s All In Your Head", "artist": "Project One", "performed": False, "year": 2008},
]

@app.on_event("startup")
async def ensure_seed():
    try:
        songs_col = collection("song")
        if songs_col.count_documents({}) == 0:
            songs_col.insert_many(DEFAULT_SONGS)
    except Exception:
        pass

# Models

class TogglePayload(BaseModel):
    token: Optional[str] = None

class CreateSessionResponse(BaseModel):
    token: str
    url: str

# Auth helper

def require_session(token: Optional[str]):
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    sess = collection("session").find_one({"token": token, "active": True})
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid or inactive token")
    return sess

# Routes

@app.get("/")
def root():
    return {"message": "Project One Setlist API running"}

@app.get("/api/songs", response_model=List[Song])
def list_songs():
    docs = get_documents("song")
    # Convert Mongo _id to str-safe by excluding
    sanitized = []
    for d in docs:
        d.pop("_id", None)
        sanitized.append(Song(**d))
    return sanitized

@app.post("/api/songs/toggle/{title}")
def toggle_song(title: str, payload: TogglePayload):
    sess = require_session(payload.token)
    # guests and hosts both allowed to toggle
    res = collection("song").find_one({"title": title})
    if not res:
        raise HTTPException(404, detail="Song not found")
    new_val = not res.get("performed", False)
    collection("song").update_one({"title": title}, {"$set": {"performed": new_val}})
    return {"title": title, "performed": new_val}

@app.post("/api/session/create", response_model=CreateSessionResponse)
def create_session(role: str = "host"):
    token = secrets.token_urlsafe(12)
    session = Session(token=token, role=role, active=True)
    create_document("session", session)
    base = os.getenv("PUBLIC_FRONTEND_URL") or os.getenv("FRONTEND_URL") or ""
    url = f"{base}?token={token}" if base else f"/"  # frontend will read token from URL
    return CreateSessionResponse(token=token, url=url)

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
