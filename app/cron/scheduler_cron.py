from apscheduler.schedulers.background import BackgroundScheduler
from instagram_api_wrapper import user_wrapper, post_wrapper
from schemas import media_schema
from models import post_model
from crud import user_crud, post_crud, media_crud
from repository import post_repository
from db.database import SessionLocal
import launch
from utils import helper


sched = BackgroundScheduler(daemon=True)
# logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
# logger = logging.getLogger()
# print = logger.info


# Fetch new reels and posts for each user
@sched.scheduled_job('cron', hour='6')
def fetch_data():
    print("Starting cron to fetch posts...")

    db = SessionLocal()
    api = launch.INSTAGRAM_API

    db_users = user_crud.list_users(db=db)
    for db_user in db_users:
        post_repository.fetch_posts(db=db, user_id=db_user.id)
    db.close()



# Fetch new reels and posts for each user
# # @sched.scheduled_job('cron', hour='7')
# # @sched.scheduled_job('interval', seconds=5)
# def extract_text_from_post():
#     print("Starting cron to apply OCR on medias...")
#
#     db = SessionLocal()
#
#     db_posts = post_crud.list_posts(db=db, submitted=False)
#     for db_post in db_posts:
#         db_medias = media_crud.lists_medias(db=db, post_id=db_post.id)
#         for db_media in db_medias:
#             if db_media.ocr_text is not None:
#                 continue
#             print(f"Fetching {db_media.content_url}")
#             ocr_text = helper.extract_text(db_media.content_url)
#             if ocr_text is None:
#                 continue
#             print(f"Set text on {db_media.id}")
#             db_media.set_ocr_text(ocr_text)
#     db.close()
