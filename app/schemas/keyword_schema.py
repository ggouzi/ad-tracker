from pydantic import BaseModel, Field


class KeywordCreate(BaseModel):
    keyword: str = Field(..., example="#sponsorise")
    ad_status_id: int = Field(..., example=-1)


class Keyword(KeywordCreate):
    id: int = Field(..., example=1)
    keyword: str = Field(..., example="#sponsorise")

    class Config:
        orm_mode = True
