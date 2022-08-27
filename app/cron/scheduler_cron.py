from apscheduler.schedulers.background import BackgroundScheduler
from crud import user_crud, post_crud, media_crud
from repository import post_repository
from db.database import SessionLocal
from models import post_model
from repository import media_repository
from datetime import datetime, timedelta


sched = BackgroundScheduler(daemon=True)


MAX_RETENTION_MEDIA_POST_DAYS = 200
MAX_RETENTION_MEDIA_POST_REELS = 10


# Fetch new reels and posts for each user
@sched.scheduled_job('cron', hour='5')
# @sched.scheduled_job('interval', seconds=15)
def fetch_data():
    print("Starting cron to fetch posts...")

    db = SessionLocal()

    db_users = user_crud.list_users(db=db)
    for db_user in db_users:
        post_repository.fetch_posts(db=db, user_id=db_user.id, apply_ocr=True)
    db.close()


# Delete media that are too old
@sched.scheduled_job('cron', hour='6')
# @sched.scheduled_job('interval', seconds=5)
def delete_old_medias():
    db = SessionLocal()

    now = datetime.today()
    post_days_ago = now - timedelta(days=MAX_RETENTION_MEDIA_POST_DAYS)
    print("Starting cron to delete old medias from POST...")

    # Do not delete post. Just delete medias
    db_posts = post_crud.list_posts(db=db, submitted=True, type=post_model.POST_TYPE, before=post_days_ago)
    for db_post in db_posts:
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        for db_media in db_medias:
            media_repository.delete_media(db=db, db_media=db_media)

    post_days_ago = now - timedelta(days=MAX_RETENTION_MEDIA_POST_REELS)
    print("Starting cron to delete old medias from REEL...")

    # Do not delete post. Just delete medias
    db_posts = post_crud.list_posts(db=db, submitted=True, type=post_model.REEL_TYPE, before=post_days_ago)
    for db_post in db_posts:
        db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
        for db_media in db_medias:
            media_repository.delete_media(db=db, db_media=db_media)

    db.close()


# Fetch new reels and posts for each user
# @sched.scheduled_job('cron', hour='7')
# @sched.scheduled_job('interval', seconds=5)
# def extract_text_from_post():
#     print("Starting cron to apply OCR on medias...")
#
#     db = SessionLocal()
#
#     db_posts = post_crud.list_posts(db=db, submitted=True)
#     for db_post in db_posts:
#         db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
#         for db_media in db_medias:
#             if db_media.ocr_text is not None:
#                 continue
#             print(f"Fetching {db_media.content_url}")
#             ocr_text = post_repository.extract_text(db_media.content_url)
#             if ocr_text is None:
#                 continue
#             print(f"Set text on {db_media.id}")
#             db_media = media_crud.set_ocr_text(db=db, media_id=db_media.id, ocr_text=ocr_text)
#     db.close()
