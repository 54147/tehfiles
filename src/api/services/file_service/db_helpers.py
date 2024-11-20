from datetime import datetime

from sqlalchemy import func
from sqlalchemy.future import select
from src.api.db_models import FileUploadPG


async def create_new_file_record(db, bucket_name, filename, file_size_bytes):
    new_file_upload = FileUploadPG(
        bucket_name=bucket_name,
        key=filename,
        file_size_bytes=file_size_bytes,
        upload_date=datetime.now(),
    )
    db.add(new_file_upload)
    await db.commit()
    await db.refresh(new_file_upload)
    return new_file_upload


async def get_last_updated_file_record(db, bucket_name):
    last_uploaded_file = await db.execute(
        select(FileUploadPG)
        .filter(FileUploadPG.bucket_name == bucket_name)
        .order_by(FileUploadPG.upload_date.desc())
        .limit(1)
    )
    last_uploaded_file = last_uploaded_file.scalars().first()
    return last_uploaded_file


async def optimized_random(db):
    count_query = select(func.count(FileUploadPG.id))
    result = await db.execute(count_query)
    total_count = result.scalar()

    if total_count == 0:
        return None

    random_offset = func.floor(func.random() * total_count)
    query = select(FileUploadPG).offset(random_offset).limit(1)

    result = await db.execute(query)
    random_file_key = result.scalars().first()
    return random_file_key
