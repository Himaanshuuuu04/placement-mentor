
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "service"
    postgres_dsn: str = ""
    mongo_uri: str = ""
    redis_host: str = "redis"
    redis_port: int = 6379
    s3_endpoint_url: str = ""
    minio_endpoint: str = ""
    aws_access_key_id: str = "admin"
    aws_secret_access_key: str = "minioadmin123"
    aws_default_region: str = "us-east-1"
    ollama_base_url: str = "http://ollama:11434"

    class Config:
        env_file = ".env"
        extra = "ignore"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.minio_endpoint and not self.s3_endpoint_url:
            self.s3_endpoint_url = self.minio_endpoint

settings = Settings()
