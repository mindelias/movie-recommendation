import pandas as pd
from sklearn.model_selection import train_test_split

PATH = "data/processed"

def main():
    ratings = pd.read_csv(f"{PATH}/ratings_filtered.csv")
    
    # Ensure we have enough data
    if len(ratings) < 1000:
        print("⚠️ Warning: Insufficient data for meaningful split")
    
    train, test = train_test_split(ratings, test_size=0.2, random_state=42)
    
    train.to_csv(f"{PATH}/train.csv", index=False)
    test.to_csv(f"{PATH}/test.csv", index=False)
    print(f"✅ Split data: Train={len(train)}, Test={len(test)}")

if __name__ == "__main__":
    main()