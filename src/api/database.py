from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.api.settings import settings

sqlalchemy_database_url: str = (
    f"postgresql://{settings.pg_username}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}"
)

engine = create_engine(sqlalchemy_database_url)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
