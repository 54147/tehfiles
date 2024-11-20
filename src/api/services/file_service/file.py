import asyncio

import random
import logging

from collections import Counter

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Depends,
    Request,
    Response,
    Query,
    HTTPException,
)
from fastapi.responses import JSONResponse

from src.api.services.file_service.storage import get_storage_handle
from src.api.services.file_service.db_helpers import (
    create_new_file_record,
    get_last_updated_file_record,
    optimized_random,
)
from src.api.database import get_db
from src.api.settings import settings

from src.api.services.file_service.schema import (
    FileUploadResponse,
    LongestLinesResponse,
    LongestLineItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
    tags=["files"],
)


async def validate_file(file: UploadFile) -> bool:
    """Validate if the uploaded file is a text file."""

    try:
        _, ext = file.filename.rsplit(".", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="File must have a valid extension.")

    if ext.lower() not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .txt, .csv, and .json files are allowed.",
        )

    if not file.content_type.startswith("text/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only text-based files are allowed.",
        )

    return True


@router.post("/upload/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db=Depends(get_db),
    storage_handle=Depends(get_storage_handle),
):
    """Uploads text files to storage"""
    await validate_file(file)

    try:
        await storage_handle.upload_file(
            file.file, settings.s3_default_bucket_name, file.filename
        )
    except Exception as e:
        logger.error(f"Failed to upload file: {file.filename}. Error: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to upload file: {file.filename}"
        )

    create_new_file_record(
        db, settings.s3_default_bucket_name, file.filename, file.size
    )

    return {"key": file.filename, "filename": file.filename}


@router.get("/list_all/")
async def list_all(storage_handle=Depends(get_storage_handle)):
    """Lists all the files that are now in storage"""
    resp = await asyncio.to_thread(storage_handle.client.list_objects_v2,
                                   Bucket=settings.s3_default_bucket_name)

    if not resp.get("Contents"):
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")

    return {"results": [fo for fo in resp["Contents"]]}


@router.get("/last_uploaded/")
async def last_uploaded(db=Depends(get_db)):
    """Returns the last uploaded file metadata"""
    last_upload = get_last_updated_file_record(db, settings.s3_default_bucket_name)
    if not last_upload:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")
    return {"results": last_upload.__dict__}


@router.get("/one_random_line/")
async def one_random_line(
    request: Request, db=Depends(get_db), storage_handle=Depends(get_storage_handle)
):
    """Returns one random line from the last uploaded file as text/plain, application/json or application/xml
    depending on the request accept header.
    If the request is application/* please include following details in the response:
    - line number
    - file name
    - the letter which occurs most often in this line"""
    accept = request.headers.get("accept")

    if not accept:
        raise HTTPException(status_code=404, detail="Header is missing: accept")

    last_upload = get_last_updated_file_record(db, settings.s3_default_bucket_name)

    if not last_upload:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")

    data = await storage_handle.download_file_data(key=last_upload.key)

    if not data:
        logger.error(
            f"File is missing in the storage: {settings.s3_default_bucket_name}/{last_upload.key}"
        )
        raise HTTPException(
            status_code=404, detail=f"File is missing in the storage: {last_upload.key}"
        )

    lines = [line.decode("utf-8") for line in data.readlines()]

    if not lines:
        raise HTTPException(status_code=400, detail="Empty file")

    random_line_number = random.randint(0, len(lines) - 1)
    random_line = lines[random_line_number]

    if accept == "application/json":
        return JSONResponse(
            content={
                "random_line": random_line,
            }
        )

    if accept == "application/xml":
        data = f"""<?xml version="1.0"?>
            <shampoo>
            <Header>
                Random Line
            </Header>
            <Body>
                {random_line}
            </Body>
            </shampoo>
            """
        return Response(content=data, media_type="application/xml")

    if accept == "application/*":
        random_line = random_line.lower()
        counter = Counter(c for c in random_line if c.isalpha())

        if not counter.items():
            raise HTTPException(status_code=400, detail="Empty file")

        most_freq_letter = max(counter.items(), key=lambda x: x[1])[0]
        resp = dict(
            line_number=random_line_number,
            filename=last_upload.key,
            most_freq_letter=most_freq_letter,
        )
        return resp

    return JSONResponse(content=random_line)


@router.get("/one_random_line_backwards/")
async def one_random_line_backwards(
    db=Depends(get_db), storage_handle=Depends(get_storage_handle)
):
    """Returns one random line from random uploaded file"""
    random_file = optimized_random(db)

    if not random_file:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")

    data = await storage_handle.download_file_data(key=random_file.key)

    if not data:
        logger.error(
            f"File is missing in the storage: {settings.s3_default_bucket_name}/{random_file.key}"
        )
        raise HTTPException(
            status_code=404, detail=f"File is missing in the storage: {random_file.key}"
        )

    lines = [line.decode("utf-8") for line in data.readlines()]

    if not lines:
        raise HTTPException(status_code=400, detail="Empty file")

    random_line_number = random.randint(0, len(lines) - 1)
    random_line_backwards = lines[random_line_number][::-1]

    return JSONResponse(content={"random_line_backwards": random_line_backwards})


@router.get("/20_longest_line_of_one_file/", response_model=LongestLinesResponse)
async def twenty_longest_lines(
    random_file: bool = Query(False),
    db=Depends(get_db),
    storage_handle=Depends(get_storage_handle),
):
    """Returns 20 longest lines from the last uploaded file. Returns from a random file if random_file is set to True."""

    if random_file:
        file_to_search = optimized_random(db)
    else:
        file_to_search = get_last_updated_file_record(
            db, settings.s3_default_bucket_name
        )

    if not file_to_search:
        raise HTTPException(status_code=404, detail="No files have been uploaded yet.")

    data = await storage_handle.download_file_data(key=file_to_search.key)

    if not data:
        logger.error(
            f"File is missing in the storage: {settings.s3_default_bucket_name}/{file_to_search.key}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"File is missing in the storage: {file_to_search.key}",
        )

    lines = [line.decode("utf-8") for line in data.readlines()]

    sorted_lines = sorted(lines, key=len, reverse=True)
    longest_20_lines = sorted_lines[:20]

    return LongestLinesResponse(
        file_key=file_to_search.key,
        lines=[LongestLineItem(line_content=l) for l in longest_20_lines],
    )
