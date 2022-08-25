from typing import Optional
from pydantic import BaseModel, Field


class MediaCommon(BaseModel):
    post_id: str = Field(..., example="1")
    content_url: str = Field(..., example="https://scontent-cdg2-1.cdninstagram.com/v/t51.2885-15")


class MediaResponse(MediaCommon):
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True


class MediaCreate(MediaCommon):
    ocr_text: Optional[str] = Field(None, example="Some text")


class Media(MediaCreate):

    class Config:
        orm_mode = True
