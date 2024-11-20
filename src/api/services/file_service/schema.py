from pydantic import BaseModel

from src.api.services.file_service.db_helpers import create_new_file_record


class FileUploadResponse(BaseModel):
    key: str
    filename: str


class FileRecord:
    def __init__(self, db, bucket_name, key, size):
        self.db = db
        self.bucket_name = bucket_name
        self.key = key
        self.size = size

    async def save(self):
        await create_new_file_record(self.db, self.bucket_name, self.key, self.size)


class LongestLineItem(BaseModel):
    line_content: str


class LongestLinesResponse(BaseModel):
    file_key: str
    lines: list[LongestLineItem]