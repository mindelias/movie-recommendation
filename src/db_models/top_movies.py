from sqlalchemy import Column, Integer, Float
from ..database.base import Base

class TopMovies(Base):
    __tablename__ = "top_movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    mean_rating = Column(Float, nullable=False)
    rating_count = Column(Integer, nullable=False)

    def __repr__(self):
        return f"TopMovies(movie_id={self.movie_id}, mean_rating={self.mean_rating}, rating_count={self.rating_count})"
