from sqlalchemy import text
from src.database.session import SessionLocal

def truncate_movie_tables():
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE ratings, movies CASCADE;"))
        db.commit()
        print("✓ ratings & movies emptied (top_movies left untouched)")
    finally:
        db.close()

if __name__ == "__main__":
    truncate_movie_tables()
    print("Done.")