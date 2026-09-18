
import logging
from shared.api import create_app
from shared.config import settings

app = create_app("agent-orchestrator")
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting agent-orchestrator service. Postgres: {settings.postgres_dsn != ''}")
