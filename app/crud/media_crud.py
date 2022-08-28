from sqlalchemy.orm import Session
from models import media_model
from schemas import media_schema
from typing import Optional


def get_media(db: Session, id: int):
    query = db.query(media_model.Media).filter(media_model.Media.id == id)
    return query.first()


def lists_medias(db: Session, post_id: str, limit: Optional[int] = None):
    query = db.query(media_model.Media).filter(media_model.Media.post_id == post_id)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def delete_media_from_post(db: Session, post_id: str):
    db.query(media_model.Media).filter(media_model.Media.post_id == post_id).delete()
    db.commit()


def delete_media(db: Session, media_id: int):
    db.query(media_model.Media).filter(media_model.Media.id == media_id).delete()
    db.commit()


def create_media(db: Session, media: media_schema.MediaCreate):
    db_media = media_model.Media(
        content_url=media.content_url,
        post_id=media.post_id,
        ocr_text=media.ocr_text
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def set_ocr_text(db: Session, media_id: int, ocr_text: str):
    db_media = db.query(media_model.Media).filter(media_model.Media.id == media_id).first()
    db_media.ocr_text = ocr_text
    db.commit()
    db.refresh(db_media)
    print(f"\nMedia {db_media.id} ocr_text set")
    return db_media


def set_content_url(db: Session, media_id: int, content_url: str):
    db_media = db.query(media_model.Media).filter(media_model.Media.id == media_id).first()
    db_media.content_url = content_url
    db.commit()
    db.refresh(db_media)
    return db_media
