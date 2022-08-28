from sqlalchemy import Column, Integer, String
from db.database import Base

AD_STATUS_BAD = -2
AD_STATUS_HIDDEN = -1
AD_STATUS_NO_AD = 0
AD_STATUS_INCORRECT = 1
AD_STATUS_LEGIT = 2


class AdStatus(Base):
    __tablename__ = "ad_statuses"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)

    def __str__(self):
        return f"ID: {self.id} - Status {self.status}"
