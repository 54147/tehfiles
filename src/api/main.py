import logging

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse


from src.api.database import engine, Base
from src.api.services.file_service.file import router as file_router


async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"Error during table creation: {e}")
        raise e

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(file_router)


@app.on_event("startup")
async def on_startup():
    await create_tables()  # Await the async function directly
    logger.info("Tables created successfully (if they didn't exist).")


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
