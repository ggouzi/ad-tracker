from sqlalchemy.orm import Session
from models import post_model
from schemas import post_schema
from datetime import datetime
from typing import Optional


def get_post(db: Session, id: str, type: Optional[str] = None):
    query = db.query(post_model.Post)
    if type:
        query = query.filter(post_model.Post.type == type)
    return query.filter(post_model.Post.id == id).first()


def list_posts(db: Session, user_id: Optional[int] = None, type: Optional[str] = None, submitted: Optional[bool] = None):
    query = db.query(post_model.Post)
    if user_id:
        query = query.filter(post_model.Post.user_id == user_id)
    if type:
        query = query.filter(post_model.Post.type == type)
    if submitted is not None:
        query = query.filter(post_model.Post.submitted == submitted)
    return query.all()


def create_post(db: Session, post: post_schema.PostCreate):
    db_post = post_model.Post(
        id=post.id,
        type=post.type,
        code=post.code,
        taken_at=post.taken_at,
        location=post.location,
        lat=post.lat,
        lng=post.lng,
        is_paid_partnership=post.is_paid_partnership,
        user_id=post.user_id,
        description=post.description,
        ad_status_id=post.ad_status_id,
        expiring_at=post.expiring_at
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def submit_post(db: Session, id: str, ad_status_id: int):
    db_post = db.query(post_model.Post).filter(post_model.Post.id == id).first()
    db_post.ad_status_id = ad_status_id
    db_post.submitted = True
    db.commit()
    db.refresh(db_post)
    return db_post
