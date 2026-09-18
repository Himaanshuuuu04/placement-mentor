
from setuptools import setup, find_packages
setup(
    name="shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi", "uvicorn", "pydantic", "pydantic-settings",
        "asgi-correlation-id", "python-json-logger", "bullmq"
    ]
)
