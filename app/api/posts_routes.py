from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from utils.status import Status
from schemas import post_schema
from models import ad_status_model, post_model
from repository import post_repository
from crud import post_crud, media_crud, user_crud
from db.database import get_db
from datetime import datetime
from utils.status import get_responses
import exceptions.CustomException
from typing import Optional


router = APIRouter()

AD_STATUSES = [ad_status_model.AD_STATUS_BAD, ad_status_model.AD_STATUS_HIDDEN, ad_status_model.AD_STATUS_INCORRECT, ad_status_model.AD_STATUS_LEGIT]


@router.get("/posts/submit", response_model=post_schema.PostResponseList, responses=get_responses([200, 500]), tags=["Posts"], description="List Posts to submit")
def list_non_submitted_posts(request: Request, db: Session = Depends(get_db)):

    db_posts = post_repository.set_ad_status_posts_by_user_id(db=db, submitted=False)
    db_posts = post_crud.list_posts(db=db, submitted=False)  # List non-submitted posts
    db_posts = post_repository.add_medias(db=db, db_posts=db_posts, limit=1)
    db_posts = post_repository.add_user(db=db, db_posts=db_posts)
    return post_schema.PostResponseList(posts=db_posts)


@router.post("/posts/apply_ocr", response_model=post_schema.PostResponseList, responses=get_responses([200, 500]), tags=["Posts"], description="Apply OCR non-submitted posts")
def apply_ocr_non_submitted_posts(request: Request, db: Session = Depends(get_db)):

    db_posts = post_repository.set_ad_status_posts_by_user_id(db=db, submitted=False)
    for db_post in db_posts:
        if db_post.type == post_model.REEL_TYPE:
            db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
            for db_media in db_medias:
                if db_media.ocr_text is None:
                    ocr_text = post_repository.extract_text(db_media.content_url)
                    db_media = media_crud.set_ocr_text(db=db, media_id=db_media.id, ocr_text=ocr_text)
    db_posts = post_repository.add_medias(db=db, db_posts=db_posts)
    db_posts = post_repository.add_user(db=db, db_posts=db_posts)
    return post_schema.PostResponseList(posts=db_posts)


@router.get("/posts/{username}/fetch", response_model=post_schema.PostResponseListMedia, responses=get_responses([200, 404, 500]), tags=["Posts"], description="FetchPosts from username")
def fetch_posts_from_username(username: str, ocr: bool, request: Request, db: Session = Depends(get_db)):

    db_user = user_crud.get_user(db=db, username=username)
    if db_user is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="User not found",
            info=f"User {username} not found"
        )

    try:
        post_repository.fetch_posts(db=db, user_id=db_user.id, apply_ocr=ocr)
    except Exception as e:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=500,
            detail="Internal Server Error",
            info=f"Error: {str(e)}"
        )
    db_posts = post_repository.set_ad_status_posts_by_user_id(db=db, user_id=db_user.id)
    db_posts_with_medias = post_repository.add_medias(db=db, db_posts=db_posts)
    return post_schema.PostResponseListMedia(posts=db_posts_with_medias)


@router.get("/posts/fetch", response_model=post_schema.PostResponseListMedia, responses=get_responses([200, 500]), tags=["Posts"], description="Fetch Posts for all users")
def fetch_posts_from_all_users(request: Request, ocr: bool, db: Session = Depends(get_db)):

    db_users = user_crud.list_users(db=db)
    post_responses = []

    for db_user in db_users:
        try:
            post_repository.fetch_posts(db=db, user_id=db_user.id, apply_ocr=ocr)
        except Exception as e:
            raise exceptions.CustomException.CustomException(
                db=db,
                status_code=500,
                detail="Internal Server Error",
                info=f"Error: {str(e)}"
            )
        db_posts = post_repository.set_ad_status_posts_by_user_id(db=db, user_id=db_user.id)
        db_posts_with_medias = post_repository.add_medias(db=db, db_posts=db_posts)
        post_responses.extend(db_posts_with_medias)
    return post_schema.PostResponseListMedia(posts=post_responses)


@router.get("/posts", response_model=post_schema.PostResponseList, responses=get_responses([200, 404, 500]), tags=["Posts"], description="Return posts of the last n days")
def list_posts(request: Request, db: Session = Depends(get_db), after: Optional[datetime] = None, before: Optional[datetime] = None, user_id: Optional[int] = None):

    if user_id is None:
        user_id = None
    else:
        user_id = [user_id]
    db_posts = post_crud.list_posts(db=db, submitted=True, after=after, before=before, ad_status_id=AD_STATUSES, user_ids=user_id)

    post_responses = []
    for db_post in db_posts:
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id, limit=1)
        db_post.user = db_user
        db_post.medias = db_medias
        post_responses.append(db_post)

    return post_schema.PostResponseList(posts=post_responses)


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
def generate_text(post_generate: post_schema.PostGenerate, request: Request, db: Session = Depends(get_db)):

    db_posts = post_crud.list_posts(db=db, submitted=True, after=post_generate.after, before=post_generate.before, ad_status_id=AD_STATUSES, user_ids=post_generate.user_ids)

    postsMap = {}
    for db_post in db_posts:
        if db_post.user_id not in postsMap:
            postsMap[db_post.user_id] = []
        postsMap[db_post.user_id].append(db_post)

    result = "Nombre de posts avec du contenu sponsorisé non/mal signalé #Influencer #instagram #Ad\n\n"
    for user_id in postsMap:
        db_user = user_crud.get_user(db=db, id=user_id)
        db_posts = postsMap[user_id]
        nb_posts_hidden_or_incorrect = len([p for p in db_posts if p.ad_status_id == -1 or p.ad_status_id == 1])
        nb_posts_correct = len([p for p in db_posts if p.ad_status_id == 2])
        nb_posts_bad = len([p for p in db_posts if p.ad_status_id == -2])

        p = "post" if (nb_posts_hidden_or_incorrect == 1) else "posts"
        if nb_posts_hidden_or_incorrect > 0:
            result += f"{db_user.username}: {nb_posts_hidden_or_incorrect}\n"
        p = "post" if (nb_posts_bad == 1) else "posts"
        if nb_posts_bad > 0:
            result += f"{db_user.username}: {nb_posts_bad} {p} avec du contenu sponsorisé malhonnête\n"
        p = "post" if (nb_posts_correct == 1) else "posts"
        if nb_posts_correct > 0:
            result += f"{db_user.username}: {nb_posts_correct} {p} avec du contenu sponsorisé correctement signalé\n"

    # Generate image
    return Status(detail=result)
