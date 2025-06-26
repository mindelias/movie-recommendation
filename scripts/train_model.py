# scripts/train_model.py

import os
from fastapi import Depends
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from surprise import SVD, Dataset, Reader
from surprise.model_selection import GridSearchCV
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
 
from src.database.session import SessionLocal
from src.db_models.top_movies import TopMovies

########################
# 1) CONFIG & PATHS
########################

TRAIN_PATH = os.path.join("data", "processed", "train.csv")
# Adjust rating scale if your data is 1–5, 0.5–5, etc.
RATING_SCALE = (0.5, 5.0)

# Output model path
MODEL_PATH = os.path.join("models", "svd_model.pkl")

# Postgres connection string (example)
# Suppose you have your DB credentials in environment variables:
DB_URL = os.getenv("DATABASE_URI", "postgresql://postgres:password@localhost:5432/my_db")

 
#######################
# 1. Load & Split Data
#######################
def load_and_split_filtered_csv():
    ratings_path = "data/processed/ratings_filtered.csv"
    df = pd.read_csv(ratings_path)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    train_path = "data/processed/train.csv"
    test_path = "data/processed/test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    return train_df, test_df

###########################
# 2. GridSearch + Final Fit
###########################
def train_svd_model(train_df):
    # Convert IDs to strings - CRITICAL FIX
    train_df["userId"] = train_df["userId"].astype(str)
    train_df["tmdbId"] = train_df["tmdbId"].astype(str)

    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(train_df[["userId", "tmdbId", "rating"]], reader)
    # print('Type of data is', len(data))

    # Grid search for best hyperparams
    
    param_grid = {
        "n_factors": [100],
        "reg_all": [0.05],
        "lr_all": [0.007],
        "random_state": [42],
        "n_epochs": [20]  # Added for better convergence
    }
    gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3)
    gs.fit(data)
    best_params = gs.best_params['rmse']
    print("Best RMSE:", gs.best_score['rmse'])
    print("Best Params:", best_params)

    # Train final model on full trainset
    full_trainset = data.build_full_trainset()
    final_model = SVD(
        n_factors=best_params["n_factors"],
        reg_all=best_params["reg_all"],
        lr_all=best_params["lr_all"],
        random_state=42
    )
    final_model.fit(full_trainset)
    return final_model

############################
# 3. Save the Model Locally
############################
def save_model(model, path="models/svd_model.pkl"):
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Saved model to {path}")

 
############################
# 4. Compute & Store Fallback
############################


def compute_popularity_fallback(train_df, min_count=10):
    """
    Return a DataFrame with columns [tmdbId, mean_rating, rating_count]
    sorted by mean_rating desc, filtered by rating_count >= min_count.
    """
    popularity = train_df.groupby("tmdbId")["rating"].agg(["mean", "count"])
    popularity.columns = ["mean_rating", "rating_count"]
    # Filter out movies with fewer than `min_count` ratings
    popularity = popularity[popularity["rating_count"] >= min_count]
    popularity.sort_values("mean_rating", ascending=False, inplace=True)

    # Reset index so we keep movieId as a column
    popularity.reset_index(inplace=True)
    return popularity



########################
# 7) STORE POPULARITY FALLBACK IN POSTGRES
########################

def store_popularity_in_db(popularity_df):
    """
    Writes the fallback data (top movies) into a Postgres table named 'top_movies'.
    Each row: movieId, mean_rating, rating_count.
    """
    db: Session =  SessionLocal()

    try:
        # 1) Clear existing data in top_movies
        db.query(TopMovies).delete()
        db.commit()

        # 2) Insert new rows
        for _, row in popularity_df.iterrows():
            record = TopMovies(
                movie_id=int(row["tmdbId"]),
                mean_rating=float(row["mean_rating"]),
                rating_count=int(row["rating_count"])
            )
            db.add(record)
        
        db.commit()
        print("Inserted popularity fallback into 'top_movies' table via SQLAlchemy.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data into top_movies: {e}")
    finally:
        db.close()
########################
# MAIN EXECUTION FLOW
########################

def main():
    # 1. Load & Split
    # train_df, test_df = load_and_split_filtered_csv()
    # Load directly from processed data
    train_df = pd.read_csv("data/processed/train.csv")

    # Critical: Ensure proper typing
    train_df["tmdbId"] = train_df["tmdbId"].fillna(-1).astype(int)
    train_df = train_df[train_df["tmdbId"] > 0]  # Filter invalid IDs

    # 2. Train
    model = train_svd_model(train_df)

    # 3. Save
    save_model(model)

    # 4. Fallback
    popularity_df = compute_popularity_fallback(train_df)
    store_popularity_in_db(popularity_df)

    print("Initial training flow complete.")
if __name__ == "__main__":
    main()
