from sqlalchemy import UUID, Column, Float, Integer, String

from ..database.base import Base


class Movies(Base):
    __tablename__ = "movies"
    movie_id = Column(Integer, primary_key=True, index=True)
    movielens_id  = Column(Integer, unique=True, index=True, nullable=True) 
    title = Column(String, nullable=False)
    genres = Column(String, nullable=True)
    release_year = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    average_rating = Column(Float, nullable=False)
    poster_path = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    rating_count = Column(Float, nullable=True)
    

    def __repr__(self):
        return f"Movies(movie_id={self.movie_id}, title={self.title}, genres={self.genres}, release_year={self.release_year}, created_at={self.created_at}, average_rating={self.average_rating}, poster_path={self.poster_path})"