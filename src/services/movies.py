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
        # Debug 1: Log rated movies
        rated_movies = [r[0] for r in rated_query.all()]
        print(f"DEBUG: User {user_id} has rated {len(rated_movies)} movies: {rated_movies}")

        # candidate_movies = (
        # self.db.query(Movies)
        # .filter(
        #     Movies.movielens_id.isnot(None),
        #     ~Movies.movie_id.in_(rated_query)
        # )
        # .all()
        # )

        candidate_movies = self.db.query(Movies).filter(
        ~Movies.movie_id.in_(rated_query)
        ).all()

         # Debug 2: Log candidate movies
        print(f"DEBUG: Found {len(candidate_movies)} candidate movies with movielens_id")
        if candidate_movies:
            print(f"DEBUG: First candidate movie: ID={candidate_movies[0].movie_id}, movielens={candidate_movies[0].movielens_id}")
        else:
            print("DEBUG: No candidate movies found")
        
        results = []
        user_str = str(user_id)

        # Debug 3: Log user string format
        print(f"DEBUG: Prediction user_id format: '{user_str}'")
        
        for movie in candidate_movies:
            try:
                # Debug 4: Log before prediction
                print(f"DEBUG: Predicting for movie {movie.movie_id} (movielens={movie.movie_id})")
                # Predict using movielens_id
                pred = MovieService._model.predict(
                    user_str, 
                    str(movie.movie_id)
                )
                # Debug 5: Log successful prediction
                print(f"DEBUG: Prediction success! User: {user_str}, Movie: {movie.movie_id}, Score: {pred.est}")

                results.append((movie.movie_id, pred.est))
            except Exception as e:
                print(f"Prediction error for movie {movie.movie_id}: {str(e)}")
                continue

        print(f"DEBUG: Unsorted results: {results}")
        results.sort(key=lambda x: x[1], reverse=True)

        # Debug 7: Log final results
        print(f"DEBUG: Top {top_n} results: {results[:top_n]}")
    
        return [m_id for m_id, _ in results[:top_n]]

     