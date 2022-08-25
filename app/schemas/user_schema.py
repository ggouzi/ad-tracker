from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    id: int = Field(..., example=6394999216)
    username: str = Field(..., example="maevaa.ghennam")
    fullname: str = Field(..., example="Maeva Ghennam")
    profile_pic_url: str = Field(..., example="https://scontent-cdt1-1.cdninstagram.com/v/t51")

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    followers_count: int = Field(..., example=3321095)
    account_type: int = Field(..., example=3)
    is_business_account: bool = Field(..., example=1)
    is_verified: bool = Field(..., example=1)
    is_private: bool = Field(..., example=1)
    updated_at: Optional[datetime] = Field(None, example="2022-10-19T20:35:02")


class User(UserCreate):

    class Config:
        orm_mode = True
