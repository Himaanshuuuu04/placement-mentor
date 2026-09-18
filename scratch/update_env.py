import re

try:
    with open('.env', 'r') as f:
        env_content = f.read()

    env_content = re.sub(r'MINIO_ROOT_USER=.*?\n', 'AWS_ACCESS_KEY_ID=test\n', env_content)
    env_content = re.sub(r'MINIO_ROOT_PASSWORD=.*?\n', 'AWS_SECRET_ACCESS_KEY=test\n', env_content)
    if 'AWS_DEFAULT_REGION' not in env_content:
        env_content += "AWS_DEFAULT_REGION=us-east-1\n"
    if 'S3_ENDPOINT_URL' not in env_content:
        env_content += "S3_ENDPOINT_URL=http://localhost:4566\n"

    with open('.env', 'w') as f:
        f.write(env_content)
except:
    pass
