from datetime import datetime, timezone
import os
from fastapi import FastAPI, HTTPException
import pickle
import pandas as pd
from sqlalchemy import DateTime

 
from .services.movies import  MovieService
from .routers import auth, movies
from .database.session import engine
from .database.base import Base, DbSession, get_db
from .schemas.user import UserCreate,  UserResponse
from .db_models.users import User
from .db_models.ratings import Ratings
from .db_models.movies import Movies


# Create all tables if not using migrations (for dev/test)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Recommender")

@app.on_event("startup")
def preload():
   MovieService.preload_model()  # <── load SVD into memory


app.include_router(auth.router)
app.include_router(movies.router)
 
# Include the auth router
# app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to My Netflix Clone!"}


# @app.post("/users", response_model=UserResponse)
# def create_user(payload: UserCreate, db: DbSession):  # type: ignore
#     # Check if email already exists
#     existing_user = db.query(User).filter(User.email == payload.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # In a real app, you should hash the password here
#     # e.g. password_hash = hash_password(user_in.password)
#     # We'll just store it as-is for demonstration
#     new_user = User(
#         username=payload.username,
#         email=payload.email,
#         password_hash=payload.password,
#         first_name=payload.first_name,
#         last_name=payload.last_name,
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user

# # ---------------------------
# # 2) READ All Users
# # ---------------------------


# @app.get("/users", response_model=list[UserResponse])
# def get_users(db:  DbSession):  # type: ignore
#     users = db.query(User).all()
#     return users



##############################
# POST /ratings
##############################
# @app.post("/ratings")
# def add_rating(user_id: str, movie_id: str, rating: float, db: DbSession): # type: ignore
#     """
#     Insert a new user rating into the 'ratings' table.
#     In real usage, you'd want authentication, etc.
#     """
#     # Check if movie exists
#     movie_exists = db.query(Movies).filter(Movies.movie_id == movie_id).first()
    
#     if not movie_exists:
#         raise HTTPException(status_code=404, detail="Movie does not exist.")
    
#     # 2. check if this user already rated this movie
#     exists = (
#         db.query(Ratings)
#         .filter(Ratings.user_id == user_id, Ratings.movie_id == movie_id)
#         .first()
#     )
#     if exists:
#         raise HTTPException(status_code=400, detail="User already rated this movie.")

#     # Insert rating
#     new_rating = Ratings(user_id=user_id, movie_id=movie_id, rating=rating, rating_date=datetime.now(timezone.utc).isoformat())
#     db.add(new_rating)
#     db.commit()
#     db.refresh(new_rating)
#     return {"message": "Rating added", "rating_id": new_rating.rating_id}

# ##############################
# # GET /recommend/{user_id}
# ##############################
# @app.get("/recommend/{user_id}")
# def get_recommendations(user_id: int, db: DbSession, top_n: int = 5): # type: ignore
#     if not svd_model:
#         raise HTTPException(status_code=503, detail="Model not loaded.")

#     recs = recommend_for_user(user_id, svd_model, db, top_n=top_n)
#     return {"user_id": user_id, "recommendations": recs}




 
