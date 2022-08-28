from sqlalchemy.orm import Session
from models import ad_status_model


def get_ad_status(db: Session, id: int):
    query = db.query(ad_status_model.AdStatus).filter(ad_status_model.AdStatus.id == id)
    return query.first()


def lists_ad_statuss(db: Session):
    return db.query(ad_status_model.AdStatus).all()
