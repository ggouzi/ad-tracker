from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_recycle=21600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=True)

Base = declarative_base()


async def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
