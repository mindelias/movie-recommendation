# Movie Recommendation System - End-to-End Pipeline
## Overview
This system provides personalized movie recommendations using collaborative filtering. It combines historical rating data from MovieLens with current movie metadata from TMDb to deliver relevant suggestions through a FastAPI service. The solution handles cold starts using popularity-based fallback recommendations.

### Key Components
1. DETAILED WORKFLOW
  - Data Processing Pipeline

  - Model Training System

  - TMDb Integration

  - Recommendation API

  - Database Schema

2. PROJECT SETUP
  - Prerequisites
  - Installation
  - Database Setup with Alembic

## Detailed Workflow

## 1. Data Preparation
Processes raw MovieLens data into training-ready format:

`PYTHONPATH=. python scripts/data_preprocessing.py`

**Steps**:
**i**. Loads movies, ratings, and links CSVs

**ii**. Merges datasets on movieId

**iii**. Filters out:

**iv**. Movies without TMDb IDs

**v**. Users with fewer than 10 ratings

**vi**. Saves processed data to data/processed/ratings_filtered.csv

## 2. Train/Test Split
Creates training and testing datasets: `PYTHONPATH=. python scripts/split_data.py`

***Process***:

**i** 80/20 train-test split
**ii**Outputs:
  - data/processed/train.csv
  - data/processed/test.csv

## 3. Model Training
Trains SVD recommendation model: `python scripts/train_model.py`

***Training Process***:

**i** Loads training data
**ii** Performs grid search for optimal hyperparameters:
**iii** Trains final SVD model with best parameters
**iv**Computes popularity-based fallback recommendations
**v**Saves:
  - Model to models/svd_model.pkl
  - Popularity data to database


## 4. Movie Catalog Update
Fetches current movies from TMDb: `python scripts/fetch_movies.py`

**Data Collection**:
**i**Pulls from 3 endpoints:
  - Now Playing

  - Popular

  - Top Rated

**ii**Processes 30-50 movies per fetch

**iii**Stores in database with schema:

 

# PROJECT SETUP

### 1. Prerequisites
 - Python 3.9+
 - PostgreSQL 13+
 - TMDb API key (set as TMDB_API_KEY environment variable)



### 2. Installation

  **Clone repository**
  git clone https://github.com/yourusername/movie-recommendation.git
  cd movie-recommendation

  **Create virtual environment**
  - python -m venv venv
  - activate the virtual environment using  `source venv/bin/activate`
  - run `pip freeze > requirements.txt` 
  - run `git init` &&  `echo "venv/" > .gitignore`
  - use this command to start/run the app  `uvicorn main:app --reload`

  **Install dependencies**
  `pip install -r requirements-dev.txt`
 


### 3. Database Setup with Alembic
  **1 Configuration**: Create an .env file in your project root:
    ***env**
    DATABASE_URI=postgresql+psycopg2://postgres:yourpassword@localhost:5432/movierecommendations
    JWT_SECRET_KEY=your_strong_secret_key
    TMDB_API_KEY=your_tmdb_api_key`

  **2 Database Creation**: Create the database via PostgreSQL CLI:
    `psql -U postgres -c "CREATE DATABASE movierecommendations;`
  
  **3 Alembic Setup**: Initialize Alembic (if it does not exist):
    `alembic init migrations`

  **4 Run All Migrations**: `alembic upgrade head` 

### 4. Load Initial Data
  **Preprocess MovieLens data**
  `python scripts/preprocess.py`

  **Train initial model**
  `python scripts/train_model.py`

  **Fetch current movies**
  `python scripts/fetch_movies.py`
   


 



 




 



 
# How to run app. Using Docker with PostgreSQL.
- Install Docker Desktop
- Run `docker compose up --build`
- Run `docker compose down` to stop all services

# How to run locally without postgres or docker.
- in database/core.py change the DATABASE_URL to sqlite
- run `uvicorn src.main:app --reload`


# How to run  alembic migrations
- modify your model then
- Create a New Alembic Revision:  run `alembic revision --autogenerate -m "Some migration message"`
- Apply the Migration to Your Database: run `alembic upgrade head` or `alembic upgrade {RevisionId}`
- Downgrade migration by running : `alembic downgrade -1`

# How to run tests.
- Run `pytest` to run all tests


Cheers!