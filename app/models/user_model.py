from sqlalchemy import Column, Integer, String, Boolean, DateTime
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    fullname = Column(String, nullable=False)
    followers_count = Column(Integer, nullable=False)
    account_type = Column(Integer, nullable=False)
    is_business_account = Column(Boolean, nullable=True)
    is_verified = Column(Boolean, nullable=True)
    is_private = Column(Boolean, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    activated = Column(Boolean, nullable=False)

    def __str__(self):
        return f"{self.id} - {self.username}"
