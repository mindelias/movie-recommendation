import os
import requests
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.db_models.movies import Movies
import uuid
from datetime import datetime, timezone 
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_and_store_recent_movies():
    # Fetch from multiple endpoints
    endpoints = [
        "now_playing", 
        "popular", 
        "top_rated"
    ]
    all_movies = []
    for endpoint in endpoints:
        url = f"https://api.themoviedb.org/3/movie/{endpoint}?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        all_movies.extend(data.get("results", []))
        print(f"Received {len(data['results'])} movies:", data["results"][0])
    
     
    

    seen_ids = set()
    unique_movies = [m for m in all_movies 
                    if m["id"] not in seen_ids 
                    and not seen_ids.add(m["id"])]
    
    print

    db: Session = SessionLocal()
    try:
        for movie in  unique_movies:
            # Skip if already exists
            exists = db.query(Movies).filter_by(movie_id=movie["id"]).first()
            if exists:
                print(f"Movie {movie['id']} already exists")
                continue

            # === NEW: Fetch IMDb ID ===
            detail_url = f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
            detail_response = requests.get(detail_url)
            detail_data = detail_response.json()
            imdb_id = detail_data.get("external_ids", {}).get("imdb_id", None)
            
            # Convert list of genre IDs to a string (you can store them any way you want)
            genres_str = ",".join(str(gid) for gid in movie.get("genre_ids", []))
            # Extract release year from release_date if present
            release_date = movie.get("release_date", "")
            # release_year = release_date[:4] if release_date else None
            release_year = int(release_date[:4]) if release_date and release_date.count('-') >= 2 else None

            # Create a new movie object
            new_movie = Movies(
                movie_id=movie["id"],
                title=movie.get("title", "Untitled"),
                genres=genres_str,
                release_year=release_year,
                created_at=  datetime.now(timezone.utc).isoformat(),
                average_rating=movie.get("vote_average", 0.0),
                poster_path=movie.get("poster_path", ""),
                overview=movie.get("overview", "No overview available"),
                rating_count=movie.get("vote_count", 0),
                movielens_id=imdb_id
            )

            db.add(new_movie)
        
            print(f"Stored movie: {new_movie}")

        # === NEW: Store MovieLens-only movies ===
        # (Add this AFTER processing TMDB movies)
        ml_movies = [
            (1806, "Paulie (1998)", "Adventure|Children|Comedy"),
            # Add other MovieLens-only movies here
        ]

        for ml_id, title, genres in ml_movies:
        # Use negative ID to indicate MovieLens origin
            if db.query(Movies).filter_by(movie_id=-ml_id).first():
                continue
                
            new_movie = Movies(
                movie_id=-ml_id,  # Negative ID = MovieLens
                title=title,
                genres=genres,
                release_year=1998,  # Example - set proper year
                created_at=datetime.now(timezone.utc).isoformat(),
                average_rating=0.0,  # Placeholder
                poster_path="",
                overview="No overview available",
                rating_count=0
            )
            db.add(new_movie)
            print(f"Stored MovieLens-only movie: {new_movie}")
        db.commit()
    except Exception as e:
        db.rollback()
        print("Error storing movies:", e)
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_store_recent_movies()
