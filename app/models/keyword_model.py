from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    ad_status_id = Column(String, ForeignKey('ad_statuses.id'))

    def __str__(self):
        return f"ID: {self.id} - Keyword {self.keyword}"
