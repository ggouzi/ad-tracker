from sqlalchemy.orm import Session
from models import user_model
from schemas import user_schema
from typing import Optional


def get_user(db: Session, id: Optional[int] = None, username: Optional[str] = None):
    query = db.query(user_model.User).filter(user_model.User.activated == True)
    if id:
        query = query.filter(user_model.User.id == id)
    if username:
        query = query.filter(user_model.User.username == username)
    return query.first()


def list_users(db: Session):
    return db.query(user_model.User).filter(user_model.User.activated == True).all()


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = user_model.User(
        id=user.id,
        username=user.username,
        fullname=user.fullname,
        followers_count=user.followers_count,
        account_type=user.account_type,
        is_business_account=user.is_business_account,
        is_verified=user.is_verified,
        is_private=user.is_private,
        profile_pic_url=user.profile_pic_url,
        updated_at=None,
        activated=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
