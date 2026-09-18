
FROM python:3.11-slim
WORKDIR /app
# Copy shared package
COPY packages/shared /app/packages/shared
# Copy service
COPY services/crawler /app/services/crawler
WORKDIR /app/services/crawler
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "main.py"]
