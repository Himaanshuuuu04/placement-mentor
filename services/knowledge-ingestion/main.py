import logging
from fastapi import Request
from shared.api import create_app
from shared.config import settings
from routers import router

app = create_app("knowledge-ingestion")
app.include_router(router, prefix="/ingestion")
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting knowledge-ingestion service.")
