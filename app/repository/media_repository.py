from crud import post_crud, media_crud, user_crud
from models import media_model
from sqlalchemy.orm import Session
from utils import medias


def delete_media(db: Session, db_media: media_model.Media):
    id = db_media.id
    s3url = db_media.content_url

    # Delete from from s3
    medias.delete_media_from_s3(s3url)

    # Delete media in database
    media_crud.delete_media(db=db, media_id=db_media.id)
    print(f"Media {id} deleted")


def get_media_user(db: Session, db_media: media_model.Media):
    db_post = post_crud.get_post(db=db, id=db_media.post_id)
    if db_post is None:
        print(f"Cannot find Post {db_media.post_id}")
        return None
    db_user = user_crud.get_user(db=db, id=db_post.user_id)
    if db_user is None:
        print(f"Cannot find User {db_post.user_id}")
    return db_user
