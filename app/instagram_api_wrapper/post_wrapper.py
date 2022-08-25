import traceback
from models import post_model
from schemas import post_schema
from utils import helper
import unidecode

TEXT_TO_FIND = ["#ad", "#sponsorise"]


def fetch_posts_by_user_id(api, user_id, type=None, count=10):
    postList = []

    if type == post_model.POST_TYPE:
        posts = api.user_feed(user_id=user_id, count=count)["items"]
    elif type == post_model.REEL_TYPE:
        posts = api.user_reel_media(user_id=user_id, count=count)["items"]
    else:
        posts = api.user_feed(user_id=user_id, count=count)["items"]
        posts += api.user_reel_media(user_id=user_id, count=count)["items"]

    for post in posts:
        location, lat, lng, description = None, None, None, None
        locBlock = post.get("location", None)
        if locBlock is not None:
            location = locBlock.get("name", None)
            lat = locBlock.get("lat", None)
            lng = locBlock.get("lng", None)

        c = post.get("caption", None)
        if c is not None:
            description = c.get("text", None)

        urls = get_content_urls(post)

        type = post_model.POST_TYPE
        if "is_reel_media" in post:
            type = post_model.REEL_TYPE

        postObj = post_schema.PostCreate(
            id=str(post.get("pk")),
            type=type,
            submitted=False,
            code=post.get("code"),
            taken_at=helper.timestamp_to_date(post["taken_at"]),
            location=location,
            lat=lat,
            lng=lng,
            is_paid_partnership=post.get("is_paid_partnership"),
            user_id=user_id,
            description=description,
            ad_status_id=analyse_ad_status(post, description),
            media_urls=urls,
            expiring_at=helper.timestamp_to_date(post.get("expiring_at"))
        )

        postList.append(postObj)
    return postList


def get_content_urls(post):
    urls = []
    if "carousel_media" in post:
        for p in post["carousel_media"]:
            urls.append(p["image_versions2"]["candidates"][0]["url"])
    elif "image_versions2" in post:
        urls.append(post["image_versions2"]["candidates"][0]["url"])
    return urls


def analyse_ad_status(post, description):
    # TODO: Work on a decent algorithm to detect ads
    ad_status_id = 0
    if post.get("is_paid_partnership"):
        ad_status_id = 2
    if description:
        if any(s in unidecode.unidecode(description.lower()) for s in TEXT_TO_FIND):
            ad_status_id = 1
    return ad_status_id
