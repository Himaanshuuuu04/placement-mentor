import os
import textwrap

services = [
    "api-gateway", "identity", "company", "question", "assessment", 
    "evaluation", "mastery", "interview", "roadmap", "agent-orchestrator", 
    "retrieval", "discovery", "crawler", "document-processor", "classifier", 
    "deduplication", "embedding", "code-execution", "realtime", "knowledge-ingestion"
]

# Ensure directories
os.makedirs("packages/shared/shared", exist_ok=True)
os.makedirs("scripts", exist_ok=True)

# 1. Write Shared Packages (Minimal)
with open("packages/shared/setup.py", "w") as f:
    f.write(textwrap.dedent("""
    from setuptools import setup, find_packages
    setup(
        name="shared",
        version="0.1.0",
        packages=find_packages(),
        install_requires=[
            "fastapi", "uvicorn", "pydantic", "pydantic-settings",
            "asgi-correlation-id", "python-json-logger", "bullmq"
        ]
    )
    """))

with open("packages/shared/shared/__init__.py", "w") as f:
    f.write("")

with open("packages/shared/shared/config.py", "w") as f:
    f.write(textwrap.dedent("""
    from pydantic_settings import BaseSettings
    
    class Settings(BaseSettings):
        app_name: str = "service"
        postgres_dsn: str = ""
        mongo_uri: str = ""
        redis_host: str = "redis"
        redis_port: int = 6379
        minio_endpoint: str = ""
        
        class Config:
            env_file = ".env"
    
    settings = Settings()
    """))

with open("packages/shared/shared/logging.py", "w") as f:
    f.write(textwrap.dedent("""
    import logging
    from pythonjsonlogger import jsonlogger
    from asgi_correlation_id import correlation_id
    
    class CorrelationIdFilter(logging.Filter):
        def filter(self, record):
            record.correlation_id = correlation_id.get() or "unknown"
            return True
            
    def setup_logging():
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(correlation_id)s %(name)s %(message)s')
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
        logger.addFilter(CorrelationIdFilter())
        return logger
    """))

with open("packages/shared/shared/errors.py", "w") as f:
    f.write(textwrap.dedent("""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "details": str(exc)}
        )
    """))

with open("packages/shared/shared/observability.py", "w") as f:
    f.write(textwrap.dedent("""
    from fastapi import APIRouter
    router = APIRouter()
    
    @router.get("/health")
    async def health():
        return {"status": "ok"}
        
    @router.get("/ready")
    async def ready():
        return {"status": "ready"}
    """))

with open("packages/shared/shared/api.py", "w") as f:
    f.write(textwrap.dedent("""
    from fastapi import FastAPI
    from asgi_correlation_id import CorrelationIdMiddleware
    from shared.logging import setup_logging
    from shared.errors import global_exception_handler
    from shared.observability import router as health_router
    
    def create_app(service_name: str) -> FastAPI:
        setup_logging()
        app = FastAPI(title=service_name)
        app.add_middleware(CorrelationIdMiddleware)
        app.add_exception_handler(Exception, global_exception_handler)
        app.include_router(health_router)
        return app
    """))

with open("packages/shared/shared/events.py", "w") as f:
    f.write(textwrap.dedent("""
    from bullmq import Queue
    from shared.config import settings
    
    def get_queue(queue_name: str):
        return Queue(queue_name, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    """))

# 2. Scaffold Services
for svc in services:
    svc_dir = f"services/{svc}"
    os.makedirs(svc_dir, exist_ok=True)
    
    with open(f"{svc_dir}/main.py", "w") as f:
        f.write(textwrap.dedent(f"""
        import logging
        from shared.api import create_app
        from shared.config import settings
        
        app = create_app("{svc}")
        logger = logging.getLogger(__name__)
        
        @app.on_event("startup")
        async def startup_event():
            logger.info(f"Starting {svc} service. Postgres: {{settings.postgres_dsn != ''}}")
        """))
        
    with open(f"{svc_dir}/requirements.txt", "w") as f:
        f.write(textwrap.dedent("""
        fastapi
        uvicorn
        pydantic
        pydantic-settings
        asgi-correlation-id
        python-json-logger
        bullmq
        -e /app/packages/shared
        """))
        
    with open(f"{svc_dir}/Dockerfile", "w") as f:
        f.write(textwrap.dedent(f"""
        FROM python:3.11-slim
        WORKDIR /app
        # Copy shared package
        COPY packages/shared /app/packages/shared
        # Copy service
        COPY services/{svc} /app/services/{svc}
        WORKDIR /app/services/{svc}
        RUN pip install --no-cache-dir -r requirements.txt
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        """))

# 3. Docker Compose & Env
docker_compose_services = ""
port_start = 8001
for svc in services:
    docker_compose_services += textwrap.dedent(f"""
  {svc}:
    build:
      context: .
      dockerfile: services/{svc}/Dockerfile
    container_name: ai_mentor_{svc}
    ports:
      - "{port_start}:8000"
    environment:
      - APP_NAME={svc}
      - POSTGRES_DSN=${{POSTGRES_DSN}}
      - MONGO_URI=${{MONGO_URI}}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MINIO_ENDPOINT=http://minio:9000
    depends_on:
      - redis
    """)
    port_start += 1

with open("docker-compose.yml", "w") as f:
    f.write(textwrap.dedent("""
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: ai_mentor_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ai_mentor}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-ai_mentor_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ai_mentor} -d ${POSTGRES_DB:-ai_mentor_db}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ai_mentor_redis
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    container_name: ai_mentor_minio
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-admin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin123}
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  crawl4ai:
    image: unclecode/crawl4ai:basic-amd64
    container_name: ai_mentor_crawl4ai
    ports:
      - "11225:11225"
""") + docker_compose_services + textwrap.dedent("""
volumes:
  postgres_data:
  minio_data:
"""))

with open(".env.example", "w") as f:
    f.write(textwrap.dedent("""
    POSTGRES_USER=ai_mentor
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=ai_mentor_db
    POSTGRES_DSN=postgresql://ai_mentor:postgres@postgres:5432/ai_mentor_db
    MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/ai_mentor?retryWrites=true&w=majority
    MINIO_ROOT_USER=admin
    MINIO_ROOT_PASSWORD=minioadmin123
    """))

# 4. Makefile
with open("Makefile", "w") as f:
    f.write(textwrap.dedent("""
    .PHONY: start stop restart logs migrate seed health test

    start:
    \tdocker compose up -d --build

    stop:
    \tdocker compose down

    restart: stop start

    logs:
    \tdocker compose logs -f

    migrate:
    \tpython3 scripts/migrate.py

    init-mongo:
    \tpython3 scripts/init_mongo.py

    seed:
    \tpython3 scripts/seed.py

    health:
    \tpython3 scripts/verify.py

    test: health
    """))

print("Scaffolding complete.")
