import launch
from instagram_api_wrapper import post_wrapper
from crud import post_crud, media_crud
from models import post_model
from schemas import media_schema
import exceptions.CustomException
import traceback
from sqlalchemy.orm import Session
import easyocr
import traceback
from utils import medias
import os
from instagram_private_api import ClientChallengeRequiredError


COOKIE_FILE = "cookie.json"


def fetch_posts(db: Session, user_id: int, apply_ocr: bool = None):

    try:
        api = launch.INSTAGRAM_API
        fetch_posts_no_error(api=api, db=db, user_id=user_id, apply_ocr=apply_ocr)
    except ClientChallengeRequiredError as e:
        print(str(e))
        # launch.INSTAGRAM_API = launch.connect(settings.env.CRAWLER2_INSTAGRAM_LOGIN, settings.env.CRAWLER2_INSTAGRAM_PASSWORD)
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
        fetch_posts_no_error(api=api, db=db, user_id=user_id, apply_ocr=apply_ocr)
    except Exception as e:
        traceback.print_exc()
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=500,
            detail="Internal Server Error",
            info=f"Error: {str(e)}"
        )


def fetch_posts_no_error(api, db: Session, user_id: int, apply_ocr: bool = False):
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
        return None if (result == "") else result.strip()
    except Exception as e:
        traceback.print_exc()
        return None
