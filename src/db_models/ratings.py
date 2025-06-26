from sqlalchemy import Column, ForeignKey, Integer, Float, String
from ..database.base import Base

class Ratings(Base):
    __tablename__ = "ratings"
    rating_id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer,  ForeignKey("users.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("movies.movie_id"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    rating_date = Column(String, nullable=False)


    def __repr__(self):
        return f"Ratings(rating_id={self.rating_id}, movie_id={self.movie_id}, user_id={self.user_id}, rating={self.rating}, rating_date={self.rating_date})"




