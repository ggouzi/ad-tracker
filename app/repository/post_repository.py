import launch
from instagram_api_wrapper import post_wrapper
from crud import keyword_crud, post_crud, media_crud, user_crud
from models import ad_status_model, post_model
from schemas import media_schema, post_schema
import traceback
from sqlalchemy.orm import Session
import easyocr
from utils import medias, helper
import os
from instagram_private_api import ClientChallengeRequiredError
from typing import List, Optional
import settings


COOKIE_FILE = "cookie.json"


def fetch_posts(db: Session, user_id: int, apply_ocr: bool = None):

    try:
        api = launch.INSTAGRAM_API
        fetch_posts_no_error(api=api, db=db, user_id=user_id, apply_ocr=apply_ocr)
    except ClientChallengeRequiredError as e:
        print(str(e))
        print(f"Deleting {COOKIE_FILE} and retrying...")
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
        launch.INSTAGRAM_API = launch.connect(settings.env.CRAWLER_INSTAGRAM_LOGIN, settings.env.CRAWLER_INSTAGRAM_PASSWORD)
        api = launch.INSTAGRAM_API
        fetch_posts_no_error(api=api, db=db, user_id=user_id, apply_ocr=apply_ocr)
    except Exception as e:
        traceback.print_exc()
        raise


def fetch_posts_no_error(api, db: Session, user_id: int, apply_ocr: bool = None):
    posts = post_wrapper.fetch_posts_by_user_id(api=api, user_id=user_id)
    for post in posts:
        db_post = post_crud.get_post(db=db, id=post.id)
        if db_post is None:
            db_post = post_crud.create_post(db=db, post=post)
            # Delete old media if needed (for testing purposes)
            media_crud.delete_media_from_post(db=db, post_id=db_post.id)

            # Create associated medias
            for url in post.media_urls:
                ocr_text = None
                if apply_ocr and db_post.type == post_model.REEL_TYPE:
                    ocr_text = extract_text(url)
                schema_media = media_schema.MediaCreate(content_url=url, post_id=db_post.id, ocr_text=ocr_text)
                db_media = media_crud.create_media(db=db, media=schema_media)
                print(f"Media {db_media.id} created")
                s3url = medias.upload_to_s3(url, str(db_media.id))
                print(f"Media {db_media.id} uploaded on s3 {s3url}")
                db_media = media_crud.set_content_url(db=db, media_id=db_media.id, content_url=s3url)
            print(f"Post {db_post.id} created")


def extract_text(image_url):
    try:
        reader = easyocr.Reader(['fr'], gpu=False)
        RST = reader.readtext(image_url)
        result = ""
        for r in RST:
            text = r[1]
            confidence = r[2]
            if confidence >= 0.5:
                result += f"{text} "
        return result.strip()
    except Exception as e:
        traceback.print_exc()
        return None


def guess_ad_status(db: Session, post: post_schema.PostResponse, keywords_bad: List[str], keywords_hidden: List[str], keywords_incorrect: List[str]):
    if post.is_paid_partnership:
        return ad_status_model.AD_STATUS_LEGIT
    if (post.type == post_model.POST_TYPE):
        return helper.analyse_ad_status(post.description, keywords_bad=keywords_bad, keywords_hidden=keywords_hidden, keywords_incorrect=keywords_incorrect)
    elif (post.type == post_model.REEL_TYPE):

        ad_status_ids = []
        db_medias = media_crud.lists_medias(db=db, post_id=post.id)
        for db_media in db_medias:
            ad_status_id = helper.analyse_ad_status(db_media.ocr_text, keywords_bad=keywords_bad, keywords_hidden=keywords_hidden, keywords_incorrect=keywords_incorrect)
            if ad_status_id != ad_status_model.AD_STATUS_NO_AD:
                ad_status_ids.append(ad_status_id)
        if len(ad_status_ids) > 0:
            return max(ad_status_ids)
    return ad_status_model.AD_STATUS_NO_AD


def set_ad_status_posts_by_user_id(db: Session, user_id: Optional[int] = None, submitted: Optional[bool] = False):
    keywords_bad = keyword_crud.list_keywords(db=db, ad_status_id=ad_status_model.AD_STATUS_BAD)
    keywords_hidden_ads = keyword_crud.list_keywords(db=db, ad_status_id=ad_status_model.AD_STATUS_HIDDEN)
    keywords_incorrect_ads = keyword_crud.list_keywords(db=db, ad_status_id=ad_status_model.AD_STATUS_INCORRECT)

    keywords_bad_str = [keyword.keyword for keyword in keywords_bad]
    keywords_hidden_str = [keyword.keyword for keyword in keywords_hidden_ads]
    keywords_incorrect_str = [keyword.keyword for keyword in keywords_incorrect_ads]

    user_ids = []
    if user_id is not None:
        user_ids = [user_id]

    db_posts = post_crud.list_posts(db=db, user_ids=user_ids, submitted=submitted)
    for db_post in db_posts:
        ad_status_id = guess_ad_status(db=db, post=db_post, keywords_bad=keywords_bad_str, keywords_hidden=keywords_hidden_str, keywords_incorrect=keywords_incorrect_str)
        if ad_status_id != ad_status_model.AD_STATUS_NO_AD:
            if ad_status_id != db_post.ad_status_id:
                print(f"Post {db_post.id} - Changing ad status ID to {ad_status_id} because keyword was found")
        db_post = post_crud.set_ad_status(db=db, id=db_post.id, ad_status_id=ad_status_id)
    return db_posts


def add_medias(db: Session, db_posts: List[post_schema.PostResponseMedia], limit: Optional[int] = None):
    for db_post in db_posts:
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id, limit=limit)
        db_post.medias = db_medias
    return db_posts


def add_user(db: Session, db_posts: List[post_schema.PostResponse]):
    for db_post in db_posts:
        db_user = user_crud.get_user(db=db, id=db_post.user_id)
        db_post.user = db_user
    return db_posts
