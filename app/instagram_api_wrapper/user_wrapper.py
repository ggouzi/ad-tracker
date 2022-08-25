import traceback
from schemas import user_schema


def get_user(api, username):
    try:
        user = api.username_info(username)["user"]
        userObj = user_schema.UserCreate(
                id=user["pk"],
                username=user["username"],
                followers_count=user["follower_count"],
                fullname=user["full_name"],
                account_type=user["account_type"],
                is_business_account=user["is_business"],
                is_verified=user["is_verified"],
                profile_pic_url=user["profile_pic_url"],
                is_private=user["is_private"]
        )
        return userObj
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        return None
