with open('docker-compose.yml', 'r') as f:
    content = f.read()

mongo_service = """  mongo:
    image: mongo:6
    container_name: ai_mentor_mongo
    ports:
    - 27017:27017
    volumes:
    - mongo_data:/data/db
"""
content = content.replace('volumes:\n  postgres_data', mongo_service + 'volumes:\n  postgres_data')
content = content.replace('  minio_data: null', '  minio_data: null\n  mongo_data: null')

with open('docker-compose.yml', 'w') as f:
    f.write(content)
