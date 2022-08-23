from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request, Form
from utils.status import Status
from instagram_api_wrapper import post_wrapper
from schemas import post_schema, media_schema
from repository import post_repository
from crud import post_crud, media_crud, user_crud
from models import post_model
from db.database import engine, get_db
from typing import Optional, List
from datetime import datetime
from utils.status import get_responses
from utils import helper
import exceptions.CustomException
import logging
import launch

router = APIRouter()


@router.get("/posts/submit", response_model=post_schema.PostResponseList, responses=get_responses([200, 500]), tags=["Posts"], description="Posts to submit")
def list_non_submitted_posts(request: Request, db: Session = Depends(get_db)):

    post_responses = []
    db_posts = post_crud.list_posts(db=db, submitted=False) # List non-submitted posts
    for db_post in db_posts:
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        if db_user.activated == False:
            continue
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)
    return post_schema.PostResponseList(posts=post_responses)


@router.get("/posts/{username}/fetch", response_model=post_schema.PostResponseListMedia, responses=get_responses([200, 500]), tags=["Posts"], description="Posts to fetch")
def fetch_posts_from_username(username: str, request: Request, db: Session = Depends(get_db)):

    db_user = user_crud.get_user(db=db, username=username)
    if db_user is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="User not found",
            info=f"User {username} not found"
        )

    post_repository.fetch_posts(db=db, user_id=db_user.id)

    post_responses = []
    db_posts = post_crud.list_posts(db=db, user_id=db_user.id)
    for db_post in db_posts:
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        db_post.medias = db_medias
        post_responses.append(db_post)
    return post_schema.PostResponseListMedia(posts=post_responses)



@router.patch("/posts/submit", response_model=post_schema.PostResponseList, responses=get_responses([200, 404, 500]), tags=["Posts"], description="Submit Posts")
def submit_posts(posts: post_schema.PostSubmitList, request: Request, db: Session = Depends(get_db)):

    for post in posts.posts:
        db_post = post_crud.get_post(db=db, id=post.id)
        if db_post is None:
            raise exceptions.CustomException.CustomException(
                db=db,
                status_code=404,
                detail="Post not found",
                info=f"Post {post.id} not found"
            )
    post_responses = []

    for post in posts.posts:
        db_post = post_crud.submit_post(db=db, id=post.id, ad_status_id=post.ad_status_id)
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)
    return post_schema.PostResponseList(posts=post_responses)
