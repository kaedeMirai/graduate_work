import logging
import uvicorn

from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from watch_together.app.config import get_settings  # noqa: F401
from watch_together.app.api.v1 import sessions
from watch_together.app.db.mongo import get_mongodb_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = get_mongodb_client(settings=get_settings())
    await mongo_client.init_db("sessions")
    yield
    await mongo_client.close_connection()


def build_app():
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.info("Starting App")

    api_app = FastAPI(
        title="WatchTogether",
        description="Api for watching films together",
        version="1.0.0",
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_app.include_router(sessions.router, prefix="/api/v1")

    return api_app


app = build_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
