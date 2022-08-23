from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    id: int = Field(..., example=6394999216)
    username: str = Field(..., example="maevaa.ghennam")
    fullname: str = Field(..., example="Maeva Ghennam")
    profile_pic_url: str = Field(..., example="https://scontent-cdt1-1.cdninstagram.com/v/t51.2885-19/279496805_524189855861438_4376161679428199289_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-cdt1-1.cdninstagram.com&_nc_cat=1&_nc_ohc=sZLy0AVgjnwAX_kq6Rn&edm=AKralEIBAAAA&ccb=7-5&oh=00_AT9PoJp5prvc3vVSIENbYT3Cw_O9cMZ6TNRBpPEfKu72nA&oe=6307B59A&_nc_sid=5e3072")

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
