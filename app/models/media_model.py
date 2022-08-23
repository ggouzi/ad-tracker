from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from db.database import Base


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True)
    content_url = Column(String, nullable=False)
    post_id = Column(String, ForeignKey('posts.id'))
    ocr_text = Column(String, nullable=True)

    def __str__(self):
        return f"ID: {self.id} - Media ID{self.post_id}"
