# import pandas as pd
# from sklearn.model_selection import train_test_split

# def main():
#     # 1) Load the cleaned ratings
#     ratings = pd.read_csv("../data/processed/ratings_filtered.csv")
    
#     # 2) Train/Test split
#     train, test = train_test_split(ratings, test_size=0.2, random_state=42)
    
#     # 3) Save outputs
#     train.to_csv("../data/processed/train.csv", index=False)
#     test.to_csv("../data/processed/test.csv", index=False)
#     print("Data split complete. Train and Test saved in data/processed/")

# if __name__ == "__main__":
#     main()



import pandas as pd

ML_PATH = "data/raw/ml-latest-small/"
SAVE_PATH = "data/processed/"

def preprocess_data():
    # Load datasets
    movies_df = pd.read_csv(f"{ML_PATH}movies.csv")
    ratings_df = pd.read_csv(f"{ML_PATH}ratings.csv")
    links_df = pd.read_csv(f"{ML_PATH}links.csv")
    
    # Merge and clean
    merged = (
        movies_df.merge(links_df, on="movieId", how="left")
                .merge(ratings_df, on="movieId", how="left")
                .dropna(subset=["tmdbId"])
    )
    
    # Filter active users
    user_activity = merged.groupby("userId")["rating"].count()
    active_users = user_activity[user_activity >= 10].index
    filtered_df = merged[merged["userId"].isin(active_users)]
    
    # Save processed data
    filtered_df.to_csv(f"{SAVE_PATH}ratings_filtered.csv", index=False)
    print(f"✅ Saved filtered data with {len(filtered_df)} rows")

if __name__ == "__main__":
    preprocess_data()