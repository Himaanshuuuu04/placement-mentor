#!/bin/bash
# Start required infra
docker compose up -d postgres redis minio mongo ollama crawl4ai
# Start our pipeline services
docker compose up -d --build knowledge-ingestion discovery crawler document-processor classifier deduplication embedding
# Wait a sec for knowledge-ingestion to be ready
sleep 3
# Run the script INSIDE knowledge-ingestion container!
docker compose exec knowledge-ingestion bash -c "python /app/scripts/e2e_ingestion.py"
