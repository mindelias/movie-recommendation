from datetime import datetime, timezone
from pathlib import Path
import pickle
import random
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..schemas.movies import Movie, RatingCreate, RatingResponse
from ..db_models.ratings import Ratings
from ..db_models.top_movies import TopMovies
from ..db_models.movies import Movies

# ROOT = Path(__file__).resolve().parents[2]        # movie-recommendation/
# MODEL_FILE = ROOT / "models" / "svd_model.pkl"

MODEL_FILE = Path("models/svd_model.pkl")

class MovieService:
    """Business logic for movie recommendations and ratings."""
    _model = None  # class-level cache

    # ── public API ─────────────────────────────────────────
    @classmethod
    def preload_model(cls) -> None:
        """Load SVD model into memory once at app start-up."""
        if MODEL_FILE.exists():
            with MODEL_FILE.open("rb") as f:
                cls._model = pickle.load(f)
            print(f"✅  Loaded SVD model from {MODEL_FILE}")  
    
    def __init__(self, db: Session):
        self.db = db

     # ── All movies ───────────────────────────────────────────
    def list_all(self) -> list[Movie]:
        rows = self.db.query(Movies).all()
        # print('Rows Movies', rows)
        return [Movie.model_validate(row) for row in rows]
        # return  rows
     

     # ── Top movies (fallback list) ───────────────────────────
    def list_top(self, limit: int = 20) -> list[Movies]:
        """
        Returns movies sorted by `mean_rating` (TopMovies table).
        If you don’t have a 'top_movies' table, compute an AVG join instead.
        """
        rows = (
            self.db.query(Movies)
            .join(TopMovies, Movies.movie_id == TopMovies.movie_id)
            .order_by(TopMovies.mean_rating.desc())
            .limit(limit)
            .all()
        )
        return [Movie.model_validate(row) for row in rows]
    
    def add_rating(self, *, user_id: UUID, data: RatingCreate) -> RatingResponse:
        # 1. Movie must exist
        if not self.db.query(Movies).filter(Movies.movie_id == data.movie_id).first():
            raise HTTPException(status_code=404, detail="Movie does not exist")


        # 2. Prevent duplicate rating
        if self.db.query(Ratings).filter(
            Ratings.user_id == user_id,
            Ratings.movie_id == data.movie_id,
        ).first():
            raise HTTPException(status_code=409, detail="User already rated this movie")


        # 3. Insert
        rating_row = Ratings(
            user_id=user_id,
            movie_id=data.movie_id,
            rating=data.rating,
            rating_date=datetime.now(timezone.utc).isoformat(),
        )
        self.db.add(rating_row)
        self.db.commit()
        self.db.refresh(rating_row)
        return RatingResponse.model_validate(rating_row)
    
    def recommend_for_user(self, user_id: UUID, top_n: int = 5) -> List[int]:
        """Return a list of movie IDs, ordered by preference."""
        # 1 Cold-start check
        rating_count = (
            self.db.query(Ratings)
            .filter(Ratings.user_id == user_id)
            .count()
        )
        print('DEBUG rating_count', rating_count)
        if rating_count < 5:
            return self._fallback(top_n)

        # 2 Personalised SVD predictions
        return self._personalised(user_id, top_n)
     
   


    # ── internal helpers ──────────────────────────────────
    def _fallback(self, top_n: int) -> List[int]:
        rows = (
            self.db.query(TopMovies)
            .order_by(TopMovies.mean_rating.desc())
            .limit(top_n)
            .all()
        )
        return [row.movie_id for row in rows]

    
    
    
    def _personalised(self, user_id: UUID, top_n: int) -> List[UUID]:
        # Get movies user HASN'T rated
        rated_query = self.db.query(Ratings.movie_id).filter(
            Ratings.user_id == user_id
        )
        candidate_movies = (
            self.db.query(Movies)
            .filter(
                Movies.movielens_id.isnot(None),
                ~Movies.movie_id.in_(rated_query)
            )
            .all()
        )
        
        results = []
        user_str = str(user_id)
        
        for movie in candidate_movies:
            try:
                # Predict using movielens_id
                pred = MovieService._model.predict(
                    user_str, 
                    str(movie.movielens_id)
                )
                results.append((movie.movie_id, pred.est))
            except Exception as e:
                print(f"Prediction error for movie {movie.movie_id}: {str(e)}")
                continue
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [m_id for m_id, _ in results[:top_n]]

    # def recommend_for_user(user_id: int, model, db: Session, top_n=5):
    #     """
    #     1. Check how many ratings user has in 'ratings' table.
    #     2. If < 5 => fallback from 'top_movies'.
    #     3. Otherwise => SVD predictions for known movie IDs from training set (or skip new ones).
    #     """
    #     # 1) Check rating count
    #     user_rating_count = db.query(Ratings).filter(Ratings.user_id == user_id).count()
    #     if user_rating_count < 5:
    #         # Cold start fallback
    #         fallback = db.query(TopMovies).order_by(TopMovies.mean_rating.desc()).limit(top_n).all()
    #         return [f.movie_id for f in fallback]
    #     else:
    #         # Seasoned user => SVD
    #         # We only predict for movies the model knows
    #         # Suppose we track known IDs in a global set or we do next best approach
    #         # For demonstration, let's do a quick approach: 
    #         candidate_movies = db.query(Movies).all()  # might be large
    #         results = []
    #         for m in candidate_movies:
    #             # The model was trained with userId & movieId from the offline set
    #             # Some might be missing. We'll try str casting
    #             try:
    #                 pred = model.predict(str(user_id), str(m.id))
    #                 results.append((m.id, pred.est))
    #             except:
    #                 # If the model can't handle this ID, skip it
    #                 pass
    #         # Sort
    #         results.sort(key=lambda x: x[1], reverse=True)
    #         return [r[0] for r in results[:top_n]]