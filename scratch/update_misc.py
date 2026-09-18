import os
import re

# Update .env.example
with open('.env.example', 'r') as f:
    env_content = f.read()

env_content = re.sub(r'MINIO_ROOT_USER=.*?\n', 'AWS_ACCESS_KEY_ID=test\n', env_content)
env_content = re.sub(r'MINIO_ROOT_PASSWORD=.*?\n', 'AWS_SECRET_ACCESS_KEY=test\n', env_content)
if 'AWS_DEFAULT_REGION' not in env_content:
    env_content += "AWS_DEFAULT_REGION=us-east-1\n"
if 'S3_ENDPOINT_URL' not in env_content:
    env_content += "S3_ENDPOINT_URL=http://localhost:4566\n"

with open('.env.example', 'w') as f:
    f.write(env_content)

# Update config.py
with open('packages/shared/shared/config.py', 'r') as f:
    config_content = f.read()

config_content = config_content.replace('minio_endpoint: str = ""', 's3_endpoint_url: str = ""\n    aws_access_key_id: str = ""\n    aws_secret_access_key: str = ""\n    aws_default_region: str = "us-east-1"')

with open('packages/shared/shared/config.py', 'w') as f:
    f.write(config_content)

# Update verify.py
with open('scripts/verify.py', 'r') as f:
    verify_content = f.read()

verify_content = verify_content.replace('verify_minio()', 'verify_localstack()')
verify_content = verify_content.replace('def verify_minio():', 'def verify_localstack():')
verify_content = verify_content.replace('MinIO', 'LocalStack')
verify_content = verify_content.replace('http://localhost:9000/minio/health/live', 'http://localhost:4566/_localstack/health')

with open('scripts/verify.py', 'w') as f:
    f.write(verify_content)

print("Misc files updated successfully.")
