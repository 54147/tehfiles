import logging

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse


from src.api.database import engine, Base
from src.api.services.file_service.file import router as file_router

Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(file_router)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        return Response(content=str(e), status_code=e.status_code)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"},
        )
