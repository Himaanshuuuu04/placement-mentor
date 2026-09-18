import asyncio
import httpx
import os
import json

async def verify_crawl4ai():
    print("\n--- Testing Crawl4AI ---")
    url = "https://example.com"
    print(f"Sending {url} to Crawl4AI...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://127.0.0.1:11225/crawl", json={"url": url}, timeout=60.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                print("Successfully extracted HTML/Markdown.")
                print(f"Markdown preview: {data.get('markdown', '')[:100]}...")
            else:
                print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Failed to connect to Crawl4AI: {e}")

async def verify_ollama():
    print("\n--- Testing Ollama (llama3) ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://127.0.0.1:11434/api/generate", json={
                "model": "llama3",
                "prompt": "Say hello world",
                "stream": False
            }, timeout=30.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Response: {resp.json().get('response', '')}")
            else:
                print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Failed to connect to Ollama: {e}")

async def verify_ollama_embeddings():
    print("\n--- Testing Ollama (nomic-embed-text) ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://127.0.0.1:11434/api/embeddings", json={
                "model": "nomic-embed-text",
                "prompt": "Test document"
            }, timeout=30.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Embedding dimensions: {len(resp.json().get('embedding', []))}")
            else:
                print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Failed to connect to Ollama embeddings: {e}")

async def main():
    print("Starting Infrastructure Verification...")
    await verify_crawl4ai()
    await verify_ollama()
    await verify_ollama_embeddings()
    print("\nVerification complete.")

if __name__ == "__main__":
    asyncio.run(main())
