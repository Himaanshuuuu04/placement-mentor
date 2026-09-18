
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "service"
    postgres_dsn: str = ""
    mongo_uri: str = ""
    redis_host: str = "redis"
    redis_port: int = 6379
    s3_endpoint_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_default_region: str = "us-east-1"
    ollama_base_url: str = "http://ollama:11434"

    class Config:
        env_file = ".env"

settings = Settings()
