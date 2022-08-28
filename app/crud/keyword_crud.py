from sqlalchemy.orm import Session
from models import keyword_model
from schemas import keyword_schema
from typing import Optional
import unidecode


def get_keyword(db: Session, id: int):
    query = db.query(keyword_model.Keyword).filter(keyword_model.Keyword.id == id)
    return query.first()


def get_keyword_by_name(db: Session, name: str):
    query = db.query(keyword_model.Keyword).filter(keyword_model.Keyword.keyword == name)
    return query.first()


def list_keywords(db: Session, ad_status_id: Optional[int] = None):
    query = db.query(keyword_model.Keyword)
    if ad_status_id:
        query = query.filter(keyword_model.Keyword.ad_status_id == ad_status_id)
    return query.all()


def delete_keyword(db: Session, keyword_id: int):
    db.query(keyword_model.Keyword).filter(keyword_model.Keyword.id == keyword_id).delete()
    db.commit()


def create_keyword(db: Session, keyword: keyword_schema.KeywordCreate):
    db_keyword = keyword_model.Keyword(
        keyword=unidecode.unidecode(keyword.keyword.lower()),
        ad_status_id=keyword.ad_status_id
    )
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword
