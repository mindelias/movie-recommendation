from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from requests import Session

from ..services.user import get_current_user,  get_users_service

from ..schemas.user import UserCreate, LoginResponse, LoginRequest, Token
from ..database.base import get_db
from ..services.auth import AuthService
 
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db=Depends(get_db)):
    return AuthService(db).signup(payload)

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db=Depends(get_db)):
    return AuthService(db).login(payload.email, payload.password)

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)    
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    res = AuthService(db).login(form.username, form.password)
    return {"access_token": res.access_token, "token_type":  'bearer'}

@router.get("/users", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
def get_users(db: Session = Depends(get_db)):
    return  get_users_service(db)

 
