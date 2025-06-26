from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..core.security import decode_access_token, hash_password, verify_password, create_access_token
from ..core.config import  settings
from ..db_models.users import User
from ..schemas import user as UserSchema
class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def signup(self, data:  UserSchema.UserCreate) -> UserSchema.UserResponse: 
        self._ensure_unique_user(data.email, data.username)
        new_user = self._create_user(data)
        return self._issue_token(new_user)

    def login(self, email: str, password: str) -> UserSchema.LoginResponse:
        user = self._authenticate_user(email, password)
        return self._issue_token(user)

    # ───────── helpers ─────────
    def _ensure_unique_user(self, email: str, username: str) -> None:
        # 1. Check if user already exists (by username or email)
        if self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first():
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already in use",
        )

    def _create_user(self, payload: UserSchema.UserCreate) -> User:
        
        user = User(
            **payload.model_dump(exclude={"password"}),
            password_hash=hash_password(payload.password),
            created_at=datetime.now(timezone.utc).isoformat(),   
            is_active="active",
            
        )
         
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def _authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return user

    def _issue_token(self, user: User) -> UserSchema.LoginResponse:
        token = create_access_token(
            {"sub": user.email, "user_id": user.id},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return UserSchema.LoginResponse(access_token=token, token_type="bearer", user=user)

    def decode_token(self, token: str) -> User | None:
        """Return the user represented by this JWT, or None if invalid/inactive."""
        try:
            payload = decode_access_token(token)
            user_id: int | None = payload.get("user_id")
            if user_id is None:
                return None
        except ValueError:
            return None                           # signature/expiry failure

        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None :
            return None
        return user