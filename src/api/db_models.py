from sqlalchemy import Column, Integer, String, DateTime

from src.api.database import Base


class FileUploadPG(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True)
    bucket_name = Column(String, nullable=False)
    key = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    upload_date = Column(DateTime, nullable=False)

