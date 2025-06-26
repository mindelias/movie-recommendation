import random

from sqlalchemy.orm import Session
from ..db_models.ratings import Ratings
from ..db_models.top_movies import TopMovies
from ..db_models.movies import Movies

def recommend_for_user(user_id: int, model, db: Session, top_n=5):
    """
    1. Check how many ratings user has in 'ratings' table.
    2. If < 5 => fallback from 'top_movies'.
    3. Otherwise => SVD predictions for known movie IDs from training set (or skip new ones).
    """
    # 1) Check rating count
    user_rating_count = db.query(Ratings).filter(Ratings.user_id == user_id).count()
    if user_rating_count < 5:
        # Cold start fallback
        fallback = db.query(TopMovies).order_by(TopMovies.mean_rating.desc()).limit(top_n).all()
        return [f.movie_id for f in fallback]
    else:
        # Seasoned user => SVD
        # We only predict for movies the model knows
        # Suppose we track known IDs in a global set or we do next best approach
        # For demonstration, let's do a quick approach: 
        candidate_movies = db.query(Movies).all()  # might be large
        results = []
        for m in candidate_movies:
            # The model was trained with userId & movieId from the offline set
            # Some might be missing. We'll try str casting
            try:
                pred = model.predict(str(user_id), str(m.id))
                results.append((m.id, pred.est))
            except:
                # If the model can't handle this ID, skip it
                pass
        # Sort
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_n]]
