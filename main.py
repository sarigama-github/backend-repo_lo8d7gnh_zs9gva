import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests

from schemas import Message, Project, Profile
from database import create_document

app = FastAPI(title="Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API = "https://api.github.com"
DEFAULT_GITHUB_USERNAME = "heyitsgautham"
DEFAULT_LINKEDIN_SLUG = "heyitsgautham"


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Models for responses
class ReposResponse(BaseModel):
    repos: List[Project]


@app.get("/profile", response_model=Profile)
def get_profile(username: Optional[str] = None):
    """Return GitHub profile basics. LinkedIn data is not scraped; provide link only."""
    user = username or DEFAULT_GITHUB_USERNAME
    try:
        r = requests.get(f"{GITHUB_API}/users/{user}", timeout=10)
        if r.status_code != 200:
            raise HTTPException(status_code=404, detail="GitHub user not found")
        data = r.json()
        profile = Profile(
            username=data.get("login"),
            name=data.get("name") or data.get("login"),
            bio=data.get("bio"),
            avatar_url=data.get("avatar_url"),
            html_url=data.get("html_url"),
            location=data.get("location"),
            blog=data.get("blog"),
            company=data.get("company"),
        )
        return profile
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting GitHub: {str(e)}")


@app.get("/repos", response_model=ReposResponse)
def get_repos(username: Optional[str] = None, limit: int = 8):
    """Return top repositories by stars for the given user."""
    user = username or DEFAULT_GITHUB_USERNAME
    try:
        r = requests.get(f"{GITHUB_API}/users/{user}/repos", params={"per_page": 100, "sort": "updated"}, timeout=10)
        if r.status_code != 200:
            raise HTTPException(status_code=404, detail="Repos not found")
        items = r.json()
        # Sort by stargazers_count desc
        items.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        projects: List[Project] = []
        for it in items[:limit]:
            projects.append(Project(
                name=it.get("name"),
                description=it.get("description"),
                url=it.get("html_url"),
                homepage=it.get("homepage"),
                stars=it.get("stargazers_count", 0),
                language=it.get("language"),
                topics=it.get("topics", []) or [],
            ))
        return {"repos": projects}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting GitHub: {str(e)}")


@app.post("/contact")
def post_contact(payload: Message):
    """Save a contact message to the database."""
    try:
        doc_id = create_document("message", payload)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
