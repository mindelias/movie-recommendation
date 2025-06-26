from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.base import get_db
from ..schemas.movies import Movie, RatingCreate, RatingResponse, Recommendations
from ..services.movies import MovieService
from ..db_models.users import User
from ..services.user import get_current_user

router = APIRouter(prefix="/movies", tags=["movies and ratings"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[Movie], status_code=status.HTTP_200_OK)
def get_all_movies(db: Session = Depends(get_db)):
    movies = MovieService(db).list_all()
    return movies

@router.get("/top", response_model=List[Movie], status_code=status.HTTP_200_OK)
def get_top_movies(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    movies = MovieService(db).list_top(limit)
    return  movies
 
@router.post("/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def rate_movie(
    payload: RatingCreate,
    current_user: User = Depends(get_current_user),  # 🔒
    db: Session = Depends(get_db),
):
    return MovieService(db).add_rating(user_id=current_user.id, data=payload)


@router.get("/recommendations", response_model=Recommendations, status_code=status.HTTP_200_OK)
def my_recommendations(
    n: int = 5,
    current_user: User = Depends(get_current_user),   # 🔒 protects the route
    db: Session = Depends(get_db),
):
    movie_ids = MovieService(db).recommend_for_user(current_user.id,  top_n=n)
    return Recommendations(user_id=current_user.id, movie_ids=movie_ids)