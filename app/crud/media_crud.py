from sqlalchemy.orm import Session
from models import media_model
from schemas import media_schema
from datetime import datetime
from typing import Optional


def get_media(db: Session, id: int):
    query = db.query(media_model.Media).filter(media_model.Media.id == id)
    return query.first()


def lists_medias(db: Session, post_id: str):
    query = db.query(media_model.Media).filter(media_model.Media.post_id == post_id)
    return query.all()


def delete_media_from_post(db: Session, post_id: str):
    db_medias = db.query(media_model.Media).filter(media_model.Media.post_id == post_id).delete()
    db.commit()
    return None


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
    db.commit(db_media)
    db.refresh(db_media)
    return db_media
