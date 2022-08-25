from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from utils.status import Status
from schemas import post_schema
from repository import post_repository
from crud import post_crud, media_crud, user_crud
from db.database import get_db
from datetime import datetime
from utils.status import get_responses
import exceptions.CustomException
from datetime import datetime
from typing import Optional


router = APIRouter()

AD_STATUSES = [-2, -1, 1]


@router.get("/posts/submit", response_model=post_schema.PostResponseList, responses=get_responses([200, 500]), tags=["Posts"], description="List Posts to submit")
def list_non_submitted_posts(request: Request, db: Session = Depends(get_db)):

    post_responses = []
    db_posts = post_crud.list_posts(db=db, submitted=False)  # List non-submitted posts
    for db_post in db_posts:
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        if not db_user.activated:
            continue
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id, limit=1)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)
    return post_schema.PostResponseList(posts=post_responses)


@router.get("/posts/{username}/fetch", response_model=post_schema.PostResponseListMedia, responses=get_responses([200, 404, 500]), tags=["Posts"], description="FetchPosts from username")
def fetch_posts_from_username(username: str, request: Request, db: Session = Depends(get_db)):

    db_user = user_crud.get_user(db=db, username=username)
    if db_user is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="User not found",
            info=f"User {username} not found"
        )

    post_repository.fetch_posts(db=db, user_id=db_user.id, apply_ocr=None)

    post_responses = []
    db_posts = post_crud.list_posts(db=db, user_ids=[db_user.id])
    for db_post in db_posts:
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        db_post.medias = db_medias
        post_responses.append(db_post)
    return post_schema.PostResponseListMedia(posts=post_responses)


@router.get("/posts/fetch", response_model=post_schema.PostResponseListMedia, responses=get_responses([200, 500]), tags=["Posts"], description="Fetch Posts for all users")
def fetch_posts_from_all_users(request: Request, db: Session = Depends(get_db)):

    db_users = user_crud.list_users(db=db)
    post_responses = []

    for db_user in db_users:
        post_repository.fetch_posts(db=db, user_id=db_user.id, apply_ocr=None)

        db_posts = post_crud.list_posts(db=db, user_ids=[db_user.id])
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
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id, limit=1)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)

    return post_schema.PostResponseList(posts=post_responses)


@router.post("/posts/generate", responses=get_responses([200, 404, 500]), tags=["Posts"], description="Generate message")
def generate_image(post_generate: post_schema.PostGenerate, request: Request, db: Session = Depends(get_db)):

    db_posts = post_crud.list_posts(db=db, submitted=True, after=post_generate.after, ad_status_id=AD_STATUSES, user_ids=post_generate.user_ids)

    postsMap = {}
    for db_post in db_posts:
        if db_post.user_id not in postsMap:
            postsMap[db_post.user_id] = []
        postsMap[db_post.user_id].append(db_post)

    result = ""
    for user_id in postsMap:
        db_user = user_crud.get_user(db=db, id=user_id)
        db_posts = postsMap[user_id]
        nb_posts_hidden_or_incorrect = len([p for p in db_posts if p.ad_status_id == -1 or p.ad_status_id == 1])
        nb_posts_correct = len([p for p in db_posts if p.ad_status_id == 2])
        nb_posts_bad = len([p for p in db_posts if p.ad_status_id == -2])

        p = "post" if (nb_posts_hidden_or_incorrect == 1) else "posts"
        if nb_posts_hidden_or_incorrect > 0:
            result += f"User {db_user.username}: {nb_posts_hidden_or_incorrect} {p} avec du contenu sponsorisé non signalé ou mal signalé\n"
        p = "post" if (nb_posts_bad == 1) else "posts"
        if nb_posts_bad > 0:
            result += f"User {db_user.username}: {nb_posts_bad} {p} avec du contenu sponsorisé malhonnête\n"
        p = "post" if (nb_posts_correct == 1) else "posts"
        if nb_posts_correct > 0:
            result += f"User {db_user.username}: {nb_posts_correct} {p} avec du contenu sponsorisé correctement signalé\n"

    # Generate image
    return Status(detail=result)


@router.get("/posts", response_model=post_schema.PostResponseList, responses=get_responses([200, 404, 500]), tags=["Posts"], description="Return posts of the last n days")
def list_posts(request: Request, db: Session = Depends(get_db), after: Optional[datetime] = None, user_id: Optional[int] = None):

    if user_id is None:
        user_id = None
    else:
        user_id = [user_id]
    db_posts = post_crud.list_posts(db=db, submitted=True, after=after, ad_status_id=AD_STATUSES, user_ids=user_id)

    post_responses = []
    for db_post in db_posts:
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id, limit=1)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)

    return post_schema.PostResponseList(posts=post_responses)
