from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MediaResponse(BaseModel):
    content_url: str = Field(..., example="https://scontent-cdg2-1.cdninstagram.com/v/t51.2885-15/299784231_591305119165204_3577590406228115834_n.jpg?stp=dst-jpg_e15_p480x480&_nc_ht=scontent-cdg2-1.cdninstagram.com&_nc_cat=104&_nc_ohc=L70IyZ3NPywAX_18qjJ&edm=ABmJApABAAAA&ccb=7-5&ig_cache_key=MjkwNjkyNzU1OTc4MTIwNjI3NA%3D%3D.2-ccb7-5&oh=00_AT9c1Rn0ui0e_Qiz_qdXHnRdV8oQ7bB3bv7EJ9XcimqGpQ&oe=63070142&_nc_sid=6136e7")

    class Config:
        orm_mode = True


class MediaCreate(MediaResponse):
    post_id: str = Field(..., example="1")
    ocr_text: Optional[str] = Field(None, example="Some text")


class Media(MediaCreate):

    class Config:
        orm_mode = True
