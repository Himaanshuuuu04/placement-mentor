import re

with open('docker-compose.yml', 'r') as f:
    content = f.read()

# The tools block was appended under volumes.
# We need to remove it from there and add it under services.
tools_block = """
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
      - MINIO_ENDPOINT=http://minio:9000
    depends_on:
      - postgres
      - redis
      - minio
"""

if "volumes.tools" in content or "tools:\n    image:" in content:
    # First, let's just find the last 'volumes:' and split
    # Since I appended it exactly at the end, I can just remove it from the end.
    idx = content.rfind("  tools:")
    if idx != -1:
        clean_content = content[:idx]
        
        # Now insert tools block under services:
        svc_idx = clean_content.find("services:")
        if svc_idx != -1:
            # find the next line after services:
            next_line_idx = clean_content.find('\n', svc_idx)
            
            final_content = clean_content[:next_line_idx+1] + tools_block + clean_content[next_line_idx+1:]
            
            with open('docker-compose.yml', 'w') as out:
                out.write(final_content)
            print("Fixed docker-compose.yml")
        else:
            print("services: not found")
    else:
        print("tools block not found")
