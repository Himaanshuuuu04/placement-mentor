from minio import Minio
from shared.config import settings
import io

minio_client = None

def init_minio():
    global minio_client
    if settings.s3_endpoint_url:
        endpoint = settings.s3_endpoint_url.replace('http://', '').replace('https://', '')
        minio_client = Minio(
            endpoint,
            access_key=settings.aws_access_key_id,
            secret_key=settings.aws_secret_access_key,
            secure=settings.s3_endpoint_url.startswith('https')
        )
        # Create buckets if they don't exist
        for bucket in ["raw", "processed"]:
            if not minio_client.bucket_exists(bucket):
                minio_client.make_bucket(bucket)

def get_minio():
    if not minio_client:
        init_minio()
    return minio_client
