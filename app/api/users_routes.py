from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from instagram_api_wrapper import user_wrapper
from schemas import user_schema
from crud import user_crud
from db.database import get_db
from typing import List
from utils.status import get_responses
import exceptions.CustomException
import launch

router = APIRouter()


@router.get("/users", response_model=List[user_schema.User], responses=get_responses([200, 500]), tags=["Users"], description="List all Users")
def list_users(request: Request, db: Session = Depends(get_db)):
    db_users = user_crud.list_users(db=db)
    return db_users


@router.get("/users/{username}", response_model=user_schema.User, responses=get_responses([200, 404, 500]), tags=["Users"], description="Get a User by username")
def get_user(username: str, request: Request, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db=db, username=username)
    if not db_user:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="User not found",
            info=f"User {username} not found"
        )
    return db_user


@router.get("/users/fetch/{username}", response_model=user_schema.User, responses=get_responses([200, 404, 500]), tags=["Users"], description="Fetch a new User by username")
def fetch_user(username: str, request: Request, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db=db, username=username)
    if db_user:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=400,
            detail="User already exists",
            info=f"User {username} already exists"
        )
    else:
        user = user_wrapper.get_user(launch.INSTAGRAM_API, username)
        db_user = user_crud.create_user(db=db, user=user)
    return db_user
