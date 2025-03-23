from typing import Annotated

from fastapi import Depends
from .session import SessionLocal
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_db():
     
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[SessionLocal, Depends(get_db)]
