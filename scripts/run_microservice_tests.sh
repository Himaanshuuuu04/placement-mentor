#!/bin/bash
# Move to project root
cd "$(dirname "$0")/.."

echo "Running Unit Tests for Microservices (bypassing BullMQ)..."

docker run --rm --network ai_mentor_default -v $(pwd):/app -w /app python:3.11-slim bash -c "pip install -e packages/shared && POSTGRES_DSN=postgresql://ai_mentor:postgres@postgres:5432/ai_mentor_db MONGO_URI=mongodb://mongo:27017 API_URL=http://knowledge-ingestion:8000/ingestion S3_ENDPOINT_URL=http://minio:9000 REDIS_HOST=redis CRAWL4AI_URL=http://crawl4ai:11225/crawl python scripts/test_microservices.py"
