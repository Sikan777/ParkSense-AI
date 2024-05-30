from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import crud, schemas
from database import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)
