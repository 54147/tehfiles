import asyncio
import logging

import io

import boto3

from src.api.settings import settings

from fastapi import HTTPException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class StorageHandle:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str):
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def _upload_file_sync(self, file_data: bytes, bucket_name: str, object_key: str):
        return self.client.upload_fileobj(file_data, bucket_name, object_key)

    async def upload_file(self, file_data, bucket_name, object_key):
        try:
            response = await asyncio.to_thread(
                self._upload_file_sync, file_data, bucket_name, object_key
            )
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def download_file_data(self, key: str):
        data = io.BytesIO()
        await asyncio.to_thread(self.client.download_fileobj,
                                Bucket=settings.s3_default_bucket_name, Key=key, Fileobj=data
                                )
        data.seek(0)
        return data


def create_storage_handle(
    endpoint_url: str = settings.s3_url,
    access_key: str = settings.s3_access_key,
    secret_key: str = settings.s3_secret_key,
):
    return StorageHandle(endpoint_url, access_key, secret_key)


# storage_handle: StorageHandle = Depends(get_storage_handle)
def get_storage_handle():
    client = create_storage_handle()
    try:
        yield client
    finally:
        pass
