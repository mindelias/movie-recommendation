from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..db_models.users import User

from ..database.base import get_db
from .auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = AuthService(db).decode_token(token)   # implement inside AuthService
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_users_service(db: Session):
    return db.query(User).all()

 


