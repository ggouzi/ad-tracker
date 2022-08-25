from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from db.database import Base

REEL_TYPE = 'reel'
POST_TYPE = 'post'


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    code = Column(String, nullable=True)
    taken_at = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    is_paid_partnership = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String, nullable=True)
    ad_status_id = Column(Integer, nullable=False)
    submitted = Column(Boolean, nullable=False, default=0)
    expiring_at = Column(DateTime, nullable=True)

    def __str__(self):
        return f"""ID: {self.id}\nCode: {self.code}\ntaken_at: {self.taken_at}
        \nLocation: {self.location}
        \nis_paid_partnership: {self.is_paid_partnership}\nuser_id: {self.user_id}\nDescription: {self.description}\n"""
