from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from crud import keyword_crud, ad_status_crud
from schemas import keyword_schema
from db.database import get_db
from utils.status import Status, get_responses
import exceptions.CustomException
from typing import List, Optional

router = APIRouter()


@router.get("/keywords/{keyword_id}", response_model=keyword_schema.Keyword, responses=get_responses([204, 404, 500]), tags=["Keywords"], description="Get keyword")
def get_keyword(keyword_id: int, request: Request, db: Session = Depends(get_db)):

    db_keyword = keyword_crud.get_keyword(db=db, id=keyword_id)
    if db_keyword is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="Keyword not found",
            info=f"Keyword {keyword_id} not found"
        )
    return db_keyword


@router.get("/keywords", response_model=List[keyword_schema.Keyword], responses=get_responses([204, 404, 500]), tags=["Keywords"], description="List keywords")
def list_keywords(request: Request, db: Session = Depends(get_db), ad_status_id: Optional[int] = None):

    db_keywords = keyword_crud.list_keywords(db=db, ad_status_id=ad_status_id)
    return db_keywords


@router.post("/keywords", responses=get_responses([200, 404, 409, 500]), tags=["Keywords"], description="Create Keyword")
def create_keyword(keyword: keyword_schema.KeywordCreate, request: Request, db: Session = Depends(get_db)):

    db_ad_status = ad_status_crud.get_ad_status(db=db, id=keyword.ad_status_id)
    if db_ad_status is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="AdStatus not found",
            info=f"AdStatus {keyword.ad_status_id} not found"
        )

    db_keyword = keyword_crud.get_keyword_by_name(db=db, name=keyword.keyword)
    if db_keyword is not None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=409,
            detail=f"Keyword {keyword.keyword} already exists",
            info=f"Keyword {keyword.keyword} already exists"
        )

    db_keyword = keyword_crud.create_keyword(db=db, keyword=keyword)
    return db_keyword


@router.delete("/keywords/{keyword_id}", responses=get_responses([204, 404, 500]), tags=["Keywords"], description="Delete keyword")
def delete_keyword(keyword_id: int, request: Request, db: Session = Depends(get_db)):

    db_keyword = keyword_crud.get_keyword(db=db, id=keyword_id)
    if db_keyword is None:
        raise exceptions.CustomException.CustomException(
            db=db,
            status_code=404,
            detail="Keyword not found",
            info=f"Keyword {keyword_id} not found"
        )
    keyword_crud.delete_keyword(db=db, keyword_id=keyword_id)
    return Status(detail=f"Keyword {keyword_id} successfully deleted")
