import os
import yaml

services = [
    "api-gateway", "identity", "company", "question", "assessment", 
    "evaluation", "mastery", "interview", "roadmap", "agent-orchestrator", 
    "retrieval", "discovery", "crawler", "document-processor", "classifier", 
    "deduplication", "embedding", "code-execution", "realtime", "knowledge-ingestion"
]

with open('docker-compose.yml', 'r') as f:
    try:
        # Load the YAML. Since those 20 services are at the root, they will be parsed as root keys.
        data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

# Move the 20 services under 'services'
if 'services' not in data:
    data['services'] = {}

for svc in services:
    if svc in data:
        data['services'][svc] = data.pop(svc)

# Also ensure 'tools' is under 'services' just in case
if 'tools' in data.get('volumes', {}):
    data['services']['tools'] = data['volumes'].pop('tools')
if 'tools' in data:
    data['services']['tools'] = data.pop('tools')

# Write back out
with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print("docker-compose.yml has been structurally fixed.")
