# PROJECT SETUP
1. Create a virtual env uisng  `python -m venv venv`


# Install all dependencies.
- Run `pip install -r requirements-dev.txt`

2. activate the virtual environment using  `source venv/bin/activate`

4. run `pip freeze > requirements.txt` 

5. run `git init` &&  `echo "venv/" > .gitignore`

6. use this command to start/run the app  `uvicorn main:app --reload`

7. use this command to run script on the terminal `PYTHONPATH=. python scripts/train_model.py` --to train model
- `PYTHONPATH=. python scripts/fetch_movies.py` --to load movies in the db
 
- `PYTHONPATH=. python scripts/train_retrain_model.py` --to train and retrain model



# Clean Architecture Template

What's included in the template?

- Domain layer with sample entities.
- Application layer with abstractions for:
  - Example use cases
  - Cross-cutting concerns (logging, validation)
- Infrastructure layer with:
  - Authentication
  - SQLAlchemy, PostgreSQL (you can change to SQLite for development in database/core.py)
  - Rate limiting on registration
- Testing projects
  - Pytest unit tests
  - Pytest integration tests (e2e tests)

I'm open to hearing your feedback about the template and what you'd like to see in future iterations. DM me on LinkedIn or email me.

--


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