import yaml
import os

with open('docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)

# Replace 'minio' with 'localstack'
if 'minio' in data['services']:
    del data['services']['minio']

data['services']['localstack'] = {
    'image': 'localstack/localstack:latest',
    'container_name': 'ai_mentor_localstack',
    'ports': ['4566:4566', '4510-4559:4510-4559'],
    'environment': [
        'SERVICES=s3',
        'DEBUG=1',
        'AWS_DEFAULT_REGION=us-east-1'
    ],
    'volumes': [
        'localstack_data:/var/lib/localstack'
    ]
}

if 'minio_data' in data.get('volumes', {}):
    del data['volumes']['minio_data']
data.setdefault('volumes', {})['localstack_data'] = None

# Update dependencies and environment variables in other services
for svc_name, svc_data in data['services'].items():
    if svc_name not in ['localstack', 'postgres', 'redis', 'crawl4ai']:
        
        # update depends_on
        if 'depends_on' in svc_data:
            if isinstance(svc_data['depends_on'], list):
                if 'minio' in svc_data['depends_on']:
                    svc_data['depends_on'].remove('minio')
                if 'localstack' not in svc_data['depends_on']:
                    svc_data['depends_on'].append('localstack')
            elif isinstance(svc_data['depends_on'], dict):
                if 'minio' in svc_data['depends_on']:
                    del svc_data['depends_on']['minio']
                svc_data['depends_on']['localstack'] = {'condition': 'service_started'}
        
        # update environment
        if 'environment' in svc_data:
            if isinstance(svc_data['environment'], list):
                new_env = []
                for env in svc_data['environment']:
                    if env.startswith('MINIO_'):
                        continue
                    new_env.append(env)
                # Add S3 endpoint
                new_env.append('S3_ENDPOINT_URL=http://localstack:4566')
                new_env.append('AWS_ACCESS_KEY_ID=test')
                new_env.append('AWS_SECRET_ACCESS_KEY=test')
                new_env.append('AWS_DEFAULT_REGION=us-east-1')
                svc_data['environment'] = new_env

with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print("docker-compose.yml updated successfully.")
