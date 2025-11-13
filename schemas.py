"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

# Portfolio-specific schemas

class Message(BaseModel):
    name: str = Field(..., description="Sender full name")
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Subject line")
    message: str = Field(..., min_length=5, max_length=5000, description="Message body")

class Project(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Short description")
    url: Optional[HttpUrl] = Field(None, description="Project or repo URL")
    homepage: Optional[HttpUrl] = Field(None, description="Live demo URL if any")
    stars: Optional[int] = Field(0, ge=0, description="GitHub stars count")
    language: Optional[str] = Field(None, description="Primary language")
    topics: Optional[List[str]] = Field(default_factory=list, description="Topics/tags")

class Profile(BaseModel):
    username: str = Field(..., description="GitHub username")
    name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[HttpUrl] = Field(None, description="Avatar image URL")
    html_url: Optional[HttpUrl] = Field(None, description="Profile URL")
    location: Optional[str] = Field(None, description="Location")
    blog: Optional[str] = Field(None, description="Website or blog")
    company: Optional[str] = Field(None, description="Company or org")
