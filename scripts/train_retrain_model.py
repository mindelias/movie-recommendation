# scripts/retrain_model.py
import pandas as pd
import pickle
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.db_models.ratings import Ratings
from src.db_models.top_movies import TopMovies  # Add this
from surprise import SVD, Dataset, Reader
from surprise.model_selection import GridSearchCV
import os  # Add this for path handling

def export_ratings_from_db():
    db: Session = SessionLocal()
    try:
        query = """
            SELECT 
                r.user_id::text AS userId,
                m.movielens_id::text AS movieId,
                r.rating
            FROM ratings r
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE m.movielens_id IS NOT NULL
        """
        df = pd.read_sql_query(query, db.connection())
        return df
    finally:
        db.close()

# Add this new function for popularity fallback
def store_popularity_in_db(popularity_df):
    """Writes the fallback data to 'top_movies' table"""
    db: Session = SessionLocal()
    try:
        # Clear existing data
        db.query(TopMovies).delete()
        db.commit()
        
        # Insert new rows
        for _, row in popularity_df.iterrows():
            record = TopMovies(
                movie_id=int(row["movieId"]),
                mean_rating=float(row["mean_rating"]),
                rating_count=int(row["rating_count"])
            )
            db.add(record)
        db.commit()
        print("✅ Popularity fallback stored in database")
    except Exception as e:
        db.rollback()
        print(f"❌ Error storing popularity: {str(e)}")
    finally:
        db.close()

def train_model():
    print("=== Starting model training ===")
    # 1) Export ratings from DB
    df = export_ratings_from_db()
    
    if df.empty:
        print("⚠️ No ratings found. Using fallback initialization")
        # Initialize empty model
        model = SVD(n_factors=100, reg_all=0.05, lr_all=0.007, random_state=42)
        with open("models/svd_model.pkl", "wb") as f:
            pickle.dump(model, f)
        print("✅ Created empty model for cold start")
        return
    
    print(f"✅ Exported {len(df)} ratings")
    print(f"Sample data:\n{df.head(2)}")

    # 2) Prepare dataset
    print("\nPreparing dataset...")
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
    print("✅ Dataset prepared")

    # 3) Grid search
    print("\nOptimizing hyperparameters...")
    param_grid = {
        "n_factors": [100],
        "reg_all": [0.05],
        "lr_all": [0.007],
        "random_state": [42]
    }
    
    gs = GridSearchCV(SVD, param_grid, measures=["rmse"], cv=3, n_jobs=-1)
    gs.fit(data)
    
    best_params = gs.best_params["rmse"]
    print(f"✅ Grid search complete")
    print(f"Best RMSE: {gs.best_score['rmse']:.4f}")
    print(f"Best Params: {best_params}")

    # 4) Train final model
    print("\nTraining model...")
    model = SVD(**best_params)
    full_trainset = data.build_full_trainset()
    model.fit(full_trainset)
    print("✅ Model trained")
    print(f"- Users: {full_trainset.n_users}")
    print(f"- Movies: {full_trainset.n_items}")
    print(f"- Ratings: {full_trainset.n_ratings}")
    
    # 5) Test prediction
    print("\nTesting sample prediction...")
    try:
        test_user = df["userId"].iloc[0]
        test_movie = df["movieId"].iloc[0]
        pred = model.predict(test_user, test_movie)
        print(f"Test prediction: User {test_user}, Movie {test_movie} → {pred.est:.2f}")
    except Exception as e:
        print(f"❌ Prediction test failed: {str(e)}")

    # 6) Save model
    print("\nSaving model...")
    os.makedirs("models", exist_ok=True)
    with open("models/svd_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("✅ Model saved to models/svd_model.pkl")

    # 7) Compute popularity fallback
    print("\nComputing popularity rankings...")
    popularity_df = df.groupby("movieId")["rating"].agg(["mean", "count"])
    popularity_df.columns = ["mean_rating", "rating_count"]
    popularity_df = popularity_df[popularity_df["rating_count"] >= 5]
    popularity_df.sort_values("mean_rating", ascending=False, inplace=True)
    popularity_df.reset_index(inplace=True)
    
    if not popularity_df.empty:
        print(f"Popularity stats:")
        print(f"- Movies: {len(popularity_df)}")
        print(f"- Top movie: {popularity_df.iloc[0]['movieId']} (rating: {popularity_df.iloc[0]['mean_rating']:.2f})")
    else:
        print("⚠️ No movies meet minimum rating count (5)")
    
    # 8) Store fallback
    store_popularity_in_db(popularity_df)
    print("\n=== Training completed successfully ===")

if __name__ == "__main__":
    train_model()