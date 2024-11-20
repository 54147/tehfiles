import logging

import boto3

from src.api.settings import settings

from fastapi import HTTPException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class StorageHandle:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str):
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    async def upload_file(self, file_data, bucket_name, object_key):
        try:
            response = self.client.upload_fileobj(file_data, bucket_name, object_key)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


def create_storage_handle(
        endpoint_url: str = settings.s3_url,
        access_key: str = settings.s3_access_key,
        secret_key: str = settings.s3_secret_key,):
    return StorageHandle(endpoint_url, access_key, secret_key)


# storage_handle: StorageHandle = Depends(get_storage_handle)
def get_storage_handle():
    client = create_storage_handle()
    try:
        yield client
    finally:
        pass