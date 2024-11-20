from datetime import datetime

from sqlalchemy import func
from src.api.db_models import FileUploadPG


def create_new_file_record(db, bucket_name, filename, file_size_bytes):
    new_file_upload = FileUploadPG(
        bucket_name=bucket_name,
        key=filename,
        file_size_bytes=file_size_bytes,
        upload_date=datetime.now(),
    )
    db.add(new_file_upload)
    db.commit()
    db.refresh(new_file_upload)
    return new_file_upload


def get_last_updated_file_record(db, bucket_name):
    last_uploaded_file = (db.query(FileUploadPG)
                          .filter(FileUploadPG.bucket_name == bucket_name)
                          .order_by(FileUploadPG.upload_date.desc())
                          .limit(1)
                          .first())

    return last_uploaded_file


def optimized_random(db):
    return db.query(FileUploadPG.key).offset(
            func.floor(
                func.random() *
                db.query(func.count(FileUploadPG.id))
            )
        ).limit(1).first()
