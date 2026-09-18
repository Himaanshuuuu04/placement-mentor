import requests

try:
    resp = requests.post("http://localhost:11225/crawl", json={"url": "https://example.com"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(e)
    
try:
    resp = requests.post("http://localhost:11225/crawl", json={"urls": "https://example.com"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(e)

