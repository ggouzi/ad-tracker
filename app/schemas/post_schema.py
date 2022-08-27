from typing import List, Optional
from pydantic import BaseModel, Field
from schemas import media_schema, user_schema
from datetime import datetime


class PostGenerate(BaseModel):
    user_ids: Optional[List[int]] = Field(None, example=[1, 2, 3])
    after: Optional[datetime] = Field(None, example="2022-08-25T00:00:00")
    before: Optional[datetime] = Field(None, example="2022-08-26T00:00:00")


class PostSubmit(BaseModel):
    id: str = Field(..., example="2897982355577570962")
    ad_status_id: int = Field(..., example=1)
    description: Optional[str] = Field(None, example="Test")
    type: str = Field(..., example="post")
    is_paid_partnership: bool = Field(..., example=1)

    class Config:
        orm_mode = True


class PostBase(PostSubmit):
    submitted: bool = Field(..., example=True)
    code: str = Field(..., example="Cg3s5kljQaS")
    taken_at: datetime = Field(..., example="2022-10-19T20:35:02")
    location: Optional[str] = Field(None, example="Mykonos, Greece")
    lat: Optional[float] = Field(None, example="43.371493")
    lng: Optional[float] = Field(None, example="1.2808413")
    user_id: int = Field(..., example=6394999216)
    expiring_at: Optional[datetime] = Field(None, example="2022-10-19T20:35:02")

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    media_urls: List[str] = Field(..., example=["aaa", "bbb"])


class Post(PostBase):

    class Config:
        orm_mode = True


class PostResponseMedia(PostSubmit):
    medias: List[media_schema.MediaResponse]


class PostResponse(PostResponseMedia):
    user: user_schema.UserBase


class PostResponseList(BaseModel):
    posts: List[PostResponse]


class PostResponseListMedia(BaseModel):
    posts: List[PostResponseMedia]


class PostSubmitList(BaseModel):
    posts: List[PostSubmit]
