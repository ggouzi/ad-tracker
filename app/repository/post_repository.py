import launch
from instagram_api_wrapper import post_wrapper
from crud import post_crud, media_crud
from schemas import media_schema
import exceptions.CustomException
import traceback
from sqlalchemy.orm import Session
import easyocr
import traceback


def fetch_posts(db: Session, user_id):
    api = launch.INSTAGRAM_API

    try:
        # Fetch posts
        posts = post_wrapper.fetch_posts_by_user_id(api=api, user_id=user_id)
        for post in posts:
            db_post = post_crud.get_post(db=db, id=post.id)
            if db_post is None:
                db_post = post_crud.create_post(db=db, post=post)
                # Delete old media if needed (for testing purposes)
                media_crud.delete_media_from_post(db=db, post_id=db_post.id)

                # Create associated medias
                for url in post.media_urls:
                    schema_media = media_schema.MediaCreate(content_url=url, post_id=db_post.id, ocr_text=None)
                    db_media = media_crud.create_media(db=db, media=schema_media)
                    if db_media is None:
                        db_media = media_crud.create_post(db=db, media=schema_media)
    except Exception as e:
        traceback.print_exc()
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=500,
            detail="Internal Server Error",
            info=f"Error: {str(e)}"
        )


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
