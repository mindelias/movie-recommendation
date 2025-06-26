from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):          # alias: RatingRequest
    """
    Payload the client sends when rating a movie.
    `user_id` is NOT supplied — we take it from the authenticated user.
    """
    movie_id: int
    rating: float = Field(..., ge=0, le=5, description="Stars 0-5 (allow halves)")

# ---------- Response ----------
class RatingResponse(BaseModel):
    rating_id: UUID
    movie_id: int
    user_id: UUID
    rating: float
    rating_date: datetime          # stored in UTC

    class Config:                       # pydantic-v1
        from_attributes = True

class Recommendations(BaseModel):
    user_id: UUID
    movie_ids: List[int]

class Movie(BaseModel):
    movie_id: int
    title: str
    genres: Optional[str] = Field(None, description="Comma-separated genre labels")
    release_year: Optional[int] = None
    created_at: datetime              # auto-parsed from ISO-string
    average_rating: float
    poster_path: Optional[str] = None
    overview: Optional[str] = None
    rating_count: Optional[float] = None
    class Config:
        from_attributes = True

     
