import textwrap

services = [
    "api-gateway", "identity", "company", "question", "assessment", 
    "evaluation", "mastery", "interview", "roadmap", "agent-orchestrator", 
    "retrieval", "discovery", "crawler", "document-processor", "classifier", 
    "deduplication", "embedding", "code-execution", "realtime", "knowledge-ingestion"
]

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
      - S3_ENDPOINT_URL=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
    depends_on:
      - redis
      - localstack
    """)
    port_start += 1

with open("docker-compose.yml", "w") as f:
    f.write(textwrap.dedent("""
version: '3.8'

services:
  tools:
    image: python:3.11-slim
    profiles: ["tools"]
    volumes:
      - .:/app
    working_dir: /app
    environment:
      - POSTGRES_DSN=${POSTGRES_DSN}
      - MONGO_URI=${MONGO_URI}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - S3_ENDPOINT_URL=http://localstack:4566
    depends_on:
      - postgres
      - redis
      - localstack

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

  localstack:
    image: localstack/localstack:latest
    container_name: ai_mentor_localstack
    ports:
      - "4566:4566"
      - "4510-4559:4510-4559"
    environment:
      - SERVICES=s3
      - DEBUG=1
      - AWS_DEFAULT_REGION=us-east-1
    volumes:
      - localstack_data:/var/lib/localstack

  crawl4ai:
    image: unclecode/crawl4ai:basic-amd64
    container_name: ai_mentor_crawl4ai
    ports:
      - "11225:11225"
""") + docker_compose_services + textwrap.dedent("""
volumes:
  postgres_data:
  localstack_data:
"""))

print("Clean docker-compose.yml generated.")
