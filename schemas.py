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

from pydantic import BaseModel, Field
from typing import Optional, List

# Project One app schemas

class Song(BaseModel):
    """
    Songs collection schema
    Collection name: "song"
    """
    title: str = Field(..., description="Song title")
    artist: str = Field("Project One", description="Artist or artist duo")
    performed: bool = Field(False, description="Whether the song has been performed live")
    year: Optional[int] = Field(None, description="Release year")

class Session(BaseModel):
    """
    Sessions collection schema
    Collection name: "session"
    """
    token: str = Field(..., description="Session token used for simple auth via QR")
    role: str = Field("guest", description="Role for permissions: host or guest")
    active: bool = Field(True, description="Whether the session is active")

# Example schemas kept for reference (unused in app runtime)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
