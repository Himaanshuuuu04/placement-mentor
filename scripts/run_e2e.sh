#!/bin/bash
# Move to project root
cd "$(dirname "$0")/.."

# Start required infra
docker compose up -d postgres redis minio mongo ollama crawl4ai
# Start our pipeline services including api-gateway
docker compose up -d --build api-gateway knowledge-ingestion discovery crawler document-processor classifier deduplication embedding
# Wait for services to be ready
sleep 5
# Run the script via a temporary container on the host network to bypass DNS flakiness
docker run --rm --network host -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install httpx asyncpg motor && POSTGRES_DSN=postgresql://ai_mentor:postgres@127.0.0.1:5432/ai_mentor_db MONGO_URI=mongodb://127.0.0.1:27017 API_URL=http://127.0.0.1:8020/ingestion python scripts/e2e_ingestion.py"
