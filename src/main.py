from fastapi import FastAPI, HTTPException
# from .routers import auth
from .database.session import engine
from .database.base import Base, DbSession, get_db
from .schemas.user import UserCreate,  UserResponse
from .db_models.users import User



# Create all tables if not using migrations (for dev/test)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Recommender")

# Include the auth router
# app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Recommender API!"}


@app.post("/users", response_model=UserResponse)
def create_user(payload: UserCreate, db: DbSession): # type: ignore
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real app, you should hash the password here
    # e.g. password_hash = hash_password(user_in.password)
    # We'll just store it as-is for demonstration
    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# ---------------------------
# 2) READ All Users
# ---------------------------
@app.get("/users", response_model=list[UserResponse])
def get_users(db:  DbSession): # type: ignore
    users = db.query(User).all()
    return users